from fastapi import APIRouter, Depends, status, BackgroundTasks
from .schemas import (
    UserCreateModel,
    UserModel,
    UserLoginModel,
    UserBooksModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from .utils import (
    create_access_token,
    decode_token,
    verify_passwd,
    create_url_safe_token,
    decode_url_safe_token,
    generate_passwd_hash,
)
from datetime import timedelta, datetime
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.mail import mail, create_message
from src.db.redis import add_jti_to_blocklist
from src.config import Config
from src.celery_tasks import send_email

router = APIRouter()
user_serv = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOEKN_EXPIRY = 2


@router.post("/send_email")
async def send_mail(emails: EmailModel):
    recipients = emails.email_addresses

    subject = "Welcome to our Bookly App.!"
    html = "<h1>Welcome to the App</h1>"

    send_email.delay(recipients, subject, html)

    return {"message": "Email sent successfully..!"}


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_Account(
    user_data: UserCreateModel,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    email = user_data.email

    user_exists = await user_serv.user_exist(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User with email {user_data.email} already exists..",
        )

    new_user = await user_serv.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify-acc/{token}"

    recipients = [email]
    subject = "Verify your Email.!"
    html_message = f"""
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    send_email.delay(recipients, subject, html_message)

    return {
        "message": "Your Bookly Account created successfully!.  please check email to verify your account...",
        "new_user": new_user,
    }


@router.get("/verify-acc/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_serv.get_user_by_email(user_email, session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User Not Found..!"
            )

        await user_serv.update_user(user, {"is_varified": True}, session)

        return JSONResponse(
            content={"message": "Account verified successfully..!"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during account verification..!"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@router.post("/login")
async def login_user(
    login_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await user_serv.get_user_by_email(email, session)
    if user is not None:
        psswd_valid = verify_passwd(password, user.password_hash)

        if psswd_valid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                },
            )

            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOEKN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login Successful..!!",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"uid": str(user.uid), "email": user.email},
                }
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Email or Password.."
    )


@router.get("/refresh_tokren")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid or expired token"
    )


@router.get("/me", response_model=UserBooksModel)
async def current_user(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    return user


@router.get("/logout")
async def revooke_token(token_details: dict = Depends(AccessTokenBearer())):

    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out successfully"}, status_code=status.HTTP_200_OK
    )


@router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    html_message = f"""
    <h1>Reset your password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset your password..!</p>
    """
    message = create_message(
        recipients=[email],
        subject="Reset your password..!",
        body=html_message,
    )

    await mail.send_message(message)
    return JSONResponse(
        content={
            "message": "Please check your email to reset password using give link..!",
        },
        status_code=status.HTTP_200_OK,
    )


@router.post("/password-reset-confirm/{token}")
async def reset_user_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_pass = passwords.new_password
    confirm_new_pass = passwords.confirm_new_password

    if new_pass != confirm_new_pass:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Password do Not Match..!"
        )

    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_serv.get_user_by_email(user_email, session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User Not Found..!"
            )

        passwd_hash = generate_passwd_hash(new_pass)
        await user_serv.update_user(user, {"password_hash": passwd_hash}, session)

        return JSONResponse(
            content={"message": "Password reset done successfully..!"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset..!"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

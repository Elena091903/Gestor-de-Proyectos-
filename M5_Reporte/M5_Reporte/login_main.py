# login_main.py
from auth_controller import AuthController
from login_view import LoginView

def main():
    auth = AuthController()
    app = LoginView(auth_ctrl=auth)
    app.mainloop()

if __name__ == '__main__':
    main()

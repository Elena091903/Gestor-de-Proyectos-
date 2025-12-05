# main_m5.py
import os

def main():
    from mongo_con import MongoConnection
    from models.m5_model import SpeedReportModel
    from controllers.m5_controller import SpeedReportController
    from views.m5_view import SpeedReportView

    conn = MongoConnection()  
    model = SpeedReportModel(conn)
    controller = SpeedReportController(model)

    app = SpeedReportView(controller)
    app.mainloop()

if __name__ == '__main__':
    main()


import os

def main():
    from mongo_con import MongoConnection
    from models.m5_model import SpeedReportModel
    from M5_Reporte.controllers.m5_controller import SpeedReportController
    from M5_Reporte.views.m5_view import SpeedReportView

    conn = MongoConnection()  
    model = SpeedReportModel(conn)
    controller = SpeedReportController(model)

    app = SpeedReportView(controller)
    app.mainloop()

if __name__ == '__main__':
    main()

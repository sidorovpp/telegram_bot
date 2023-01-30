import win32serviceutil
import win32service
import asyncio
from time import sleep
from main import start, run_cicle, run_polling


class AppServerSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "VKBTelegramService"
    _svc_display_name_ = "VKB Telegram Service"
    _csv_description_ = "Сервис Telegram для работы с ВКБ"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.running = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        self.running = True
        self.main()

    def main(self):
        app = start()
        asyncio.run(run_cicle(app))
        while self.running:
            sleep(1)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)

import frida  
import sys  
import time
import xlwt
import signal
import os

def now():
    """ get current time"""

    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def print_msg(msg):
    """format print message

    :param msg: message
    :return:
    """

    print("[*] {now} {msg}".format(now=now(), msg=str(msg)))

def on_message(message, payload):  
    if message["type"] == "error":
        print(message)
        os.kill(os.getpid(), signal.SIGTERM)
        exit()
    if message['type'] == 'send':
        data = message["payload"]
        if data["type"] == "notice":
            alert_time = data['time']
            action = data['action']
            arg = data['arg']
            messages = data['messages']
            stacks = data['stacks']
            result = data['result']

            global excel_data
            excel_data.append({
                'alert_time': alert_time,
                'action': action,
                'messages': messages,
                'arg': arg,
                'stacks': stacks,
                'result': result,
            })

def write_xlsx(data, file_name):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('User_data_collected')

    title_style = xlwt.XFStyle()
    title_font = xlwt.Font()
    title_font.bold = True  
    title_font.height = 30 * 11
    title_style.font = title_font

    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    title_style.alignment = alignment

    worksheet.write(0, 0, '时间点', title_style)
    worksheet.col(0).width = 20 * 300
    worksheet.row(0).height_mismatch = True
    worksheet.row(0).height = 20 * 25
    worksheet.write(0, 1, '操作行为', title_style)
    worksheet.col(1).width = 20 * 300
    worksheet.write(0, 2, '行为描述', title_style)
    worksheet.col(2).width = 20 * 400
    worksheet.write(0, 3, '传入参数', title_style)
    worksheet.col(3).width = 20 * 400
    worksheet.write(0, 4, '调用堆栈', title_style)
    worksheet.col(4).width = 20 * 1200
    worksheet.write(0, 5, '函数返回值', title_style)
    worksheet.col(5).width = 20 * 400

    content_style = xlwt.XFStyle()
    content_font = xlwt.Font()
    content_font.height = 20 * 11
    content_style.font = content_font
    content_style.alignment = alignment
    content_style.alignment.wrap = 1
    for i, ed in enumerate(data):
        index_row = i + 1
        worksheet.write(index_row, 0, ed['alert_time'], content_style)
        worksheet.write(index_row, 1, ed['action'], content_style)
        worksheet.write(index_row, 2, ed['messages'], content_style)
        worksheet.write(index_row, 3, ed['arg'], content_style)
        worksheet.write(index_row, 4, ed['stacks'], content_style)
        worksheet.write(index_row, 5, ed['result'], content_style)
    workbook.save(file_name)


try:
    '''
    spawn
    '''
    excel_data = []
    device=frida.get_remote_device()
    pid=device.spawn(['com.UCMobile']) # package name
    device.resume(pid)
    time.sleep(1)
    session = device.attach(pid)

    with open("./hook.js", encoding="utf-8") as f:
        script_read = f.read()

    script_read += "setImmediate(main);\n"

    script = session.create_script(script_read)
    script.on('message', on_message)  
    script.load()  
    time.sleep(1)

    def stop(signum, frame):
        print_msg('You have stoped hook.')
        session.detach()
        global excel_data
        write_xlsx(excel_data, 'E:\RADS-Check\demo.xls') # path to save the excel file
        exit()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    sys.stdin.read()
finally:
    exit()

import datetime


def get_brands(query, worksheet):
    values_list = worksheet.col_values(1)
    brands = []
    for i, v in enumerate(values_list):
        if query.lower() in v.lower() or v.lower() in query.lower():
            brands.append((v, i + 1))
    return brands

def get_manager_info(manager_row, worksheet_main, worksheet_buyers):
    manager = worksheet_main.cell(manager_row, 2).value
    row = worksheet_buyers.find(manager).row
    nickname, phonenumber = worksheet_buyers.cell(row, 4).value, worksheet_buyers.cell(row, 5).value
    return manager, nickname, phonenumber

def send_feedback(worksheet_buyers, worksheet_feedbacks, user_info, msg_id, feedback_text, feedback_type, buyer=None):
    cur_row = len(worksheet_feedbacks.col_values(1))+1

    sender = worksheet_buyers.find(user_info['nick'])
    if sender:
        full_name = worksheet_buyers.cell(sender.row, 1).value
    else:
        full_name = f"{user_info['firstName']} {user_info['lastName']}"

    # Add row with question to Gsheet
    worksheet_feedbacks.update_cell(cur_row, 1, cur_row)
    worksheet_feedbacks.update_cell(cur_row, 2, str(datetime.datetime.now()))
    worksheet_feedbacks.update_cell(cur_row, 3, user_info['userId'])
    worksheet_feedbacks.update_cell(cur_row, 4, full_name)
    worksheet_feedbacks.update_cell(cur_row, 6, msg_id)
    worksheet_feedbacks.update_cell(cur_row, 7, feedback_type)  # тип обращения
    worksheet_feedbacks.update_cell(cur_row, 8, feedback_text)
    if buyer:
        worksheet_feedbacks.update_cell(cur_row, 9, buyer)

def get_all_buyers(worksheet):
    workers = worksheet.col_values(1)[1:]  # without column name
    buyers = []
    workers_roles = worksheet.col_values(2)[1:]  # without column name
    for i, worker in enumerate(workers):
        if workers_roles[i] == "Закупки":
            buyers.append(worker)
    return buyers

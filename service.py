

def validate_and_add_account(listbox, login_id, password, nickname):
    # 여기에 유효성 검사 로직 추가 (예: 빈 문자열 검사)
    if login_id and password and nickname:
        account_info = f"{login_id}, {password}, {nickname}"
        listbox.insert('end', account_info)
        return True
    return False

def delete_selected_account_from_listbox(listbox):
    try:
        selected_index = listbox.curselection()[0]
        listbox.delete(selected_index)
    except IndexError:
        pass  # No item is selected.


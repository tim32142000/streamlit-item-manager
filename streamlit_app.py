"""Single-page Streamlit UI for managing items."""

import streamlit as st

import database

st.set_page_config(page_title="物品管理系統", page_icon="📦", layout="centered")


def set_flash(message: str, kind: str = "success") -> None:
    st.session_state["flash"] = (kind, message)


def show_flash() -> None:
    flash = st.session_state.pop("flash", None)
    if flash:
        kind, message = flash
        getattr(st, kind)(message)


def clear_actions() -> None:
    st.session_state["editing_id"] = None
    st.session_state["deleting_id"] = None
    st.session_state["reset_confirm"] = False


try:
    database.initialize_database()
except Exception as error:
    st.error(f"資料庫初始化失敗：{error}")
    st.stop()

st.title("物品管理系統")
show_flash()

st.subheader("新增商品")
with st.form("create_item_form", clear_on_submit=True):
    new_name = st.text_input("商品名稱")
    create_col_1, create_col_2 = st.columns(2)
    with create_col_1:
        new_price = st.number_input("價格", min_value=0, step=1)
    with create_col_2:
        new_quantity = st.number_input("數量", min_value=0, step=1)
    create_submitted = st.form_submit_button("新增商品", type="primary")

if create_submitted:
    try:
        database.create_item(new_name, int(new_price), int(new_quantity))
        clear_actions()
        set_flash("商品新增成功")
        st.rerun()
    except ValueError as error:
        st.error(str(error))
    except Exception as error:
        st.error(f"新增商品失敗：{error}")

st.divider()
title_col, reset_col = st.columns([3, 1])
with title_col:
    st.subheader("商品列表")
with reset_col:
    if st.button("重設範例資料", use_container_width=True):
        clear_actions()
        st.session_state["reset_confirm"] = True
        st.rerun()

if st.session_state.get("reset_confirm", False):
    st.warning("這會刪除目前所有商品，並恢復三筆範例資料。確定要繼續嗎？")
    reset_yes_col, reset_no_col, _ = st.columns([1, 1, 2])
    with reset_yes_col:
        if st.button("確認重設", type="primary", use_container_width=True):
            try:
                database.reset_sample_items()
                clear_actions()
                set_flash("範例資料已重設")
                st.rerun()
            except Exception as error:
                st.error(f"重設失敗：{error}")
    with reset_no_col:
        if st.button("取消", key="cancel_reset", use_container_width=True):
            st.session_state["reset_confirm"] = False
            st.rerun()

items = database.list_items()

header_name, header_price, header_quantity, header_actions = st.columns([3, 1, 1, 2])
header_name.markdown("**商品名稱**")
header_price.markdown("**價格**")
header_quantity.markdown("**數量**")
header_actions.markdown("**操作**")

if not items:
    st.info("目前沒有商品，可以從上方新增或重設範例資料。")

for item in items:
    item_id = int(item["id"])
    row_name, row_price, row_quantity, row_actions = st.columns([3, 1, 1, 2])
    row_name.write(item["name"])
    row_price.write(item["price"])
    row_quantity.write(item["quantity"])
    edit_col, delete_col = row_actions.columns(2)

    with edit_col:
        if st.button("編輯", key=f"edit_{item_id}", use_container_width=True):
            clear_actions()
            st.session_state["editing_id"] = item_id
            st.rerun()
    with delete_col:
        if st.button("刪除", key=f"delete_{item_id}", use_container_width=True):
            clear_actions()
            st.session_state["deleting_id"] = item_id
            st.rerun()

    if st.session_state.get("editing_id") == item_id:
        with st.form(f"edit_item_form_{item_id}"):
            st.markdown(f"**編輯：{item['name']}**")
            edit_name = st.text_input(
                "商品名稱", value=str(item["name"]), key=f"name_{item_id}"
            )
            edit_input_col_1, edit_input_col_2 = st.columns(2)
            with edit_input_col_1:
                edit_price = st.number_input(
                    "價格",
                    min_value=0,
                    step=1,
                    value=int(item["price"]),
                    key=f"price_{item_id}",
                )
            with edit_input_col_2:
                edit_quantity = st.number_input(
                    "數量",
                    min_value=0,
                    step=1,
                    value=int(item["quantity"]),
                    key=f"quantity_{item_id}",
                )
            save_col, cancel_col = st.columns(2)
            save_edit = save_col.form_submit_button(
                "儲存", type="primary", use_container_width=True
            )
            cancel_edit = cancel_col.form_submit_button(
                "取消", use_container_width=True
            )

        if save_edit:
            try:
                updated = database.update_item(
                    item_id, edit_name, int(edit_price), int(edit_quantity)
                )
                if not updated:
                    raise ValueError("找不到要修改的商品")
                clear_actions()
                set_flash("商品修改成功")
                st.rerun()
            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                st.error(f"修改商品失敗：{error}")
        if cancel_edit:
            st.session_state["editing_id"] = None
            st.rerun()

    if st.session_state.get("deleting_id") == item_id:
        st.warning(f"確定要刪除「{item['name']}」嗎？")
        confirm_delete_col, cancel_delete_col, _ = st.columns([1, 1, 2])
        with confirm_delete_col:
            if st.button("確認刪除", key=f"confirm_delete_{item_id}", type="primary"):
                try:
                    deleted = database.delete_item(item_id)
                    if not deleted:
                        raise ValueError("找不到要刪除的商品")
                    clear_actions()
                    set_flash("商品刪除成功")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
                except Exception as error:
                    st.error(f"刪除商品失敗：{error}")
        with cancel_delete_col:
            if st.button("取消", key=f"cancel_delete_{item_id}"):
                st.session_state["deleting_id"] = None
                st.rerun()

    st.divider()

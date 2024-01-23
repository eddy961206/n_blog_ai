import unittest
import tkinter as tk
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from settings_tab import SettingsTab


class SettingsTabTest(unittest.TestCase):
    def setUp(self):
        # 테스트용 루트 윈도우 생성
        self.root = tk.Tk()
        self.settings_tab = SettingsTab(self.root)

    def tearDown(self):
        # 테스트 종료 후 루트 윈도우 종료
        self.root.destroy()

    def test_checkboxes_enabled(self):
        # 체크박스 상태가 해제되어 있는지 확인
        self.assertTrue(self.settings_tab.neighbor_feed_chkbox['state'] == 'normal')
        self.assertTrue(self.settings_tab.keyword_search_chkbox['state'] == 'normal')

    def test_checkboxes_disabled(self):
        # 체크박스를 비활성화하고 상태가 disabled인지 확인
        self.settings_tab.neighbor_feed_chkbox.deselect()
        self.settings_tab.keyword_search_chkbox.deselect()

        self.assertTrue(self.settings_tab.neighbor_feed_chkbox['state'] == 'disabled')
        self.assertTrue(self.settings_tab.keyword_search_chkbox['state'] == 'disabled')

    def test_get_user_input_datas_enabled(self):
        # 체크박스가 활성화된 상태에서 get_user_input_datas를 호출하고 결과를 확인
        self.assertTrue(self.settings_tab.neighbor_feed_chkbox['state'] == 'normal')
        self.assertTrue(self.settings_tab.keyword_search_chkbox['state'] == 'normal')

        user_input_data = self.settings_tab.get_user_input_datas()
        self.assertEqual(user_input_data[4], 1)  # feed_blog_count
        self.assertEqual(user_input_data[5], 'keyword')  # keyword
        self.assertEqual(user_input_data[6], 2)  # keyword_blog_count

    def test_get_user_input_datas_disabled(self):
        # 체크박스를 비활성화하고 get_user_input_datas를 호출하고 결과를 확인
        self.settings_tab.neighbor_feed_chkbox.deselect()
        self.settings_tab.keyword_search_chkbox.deselect()

        self.assertTrue(self.settings_tab.neighbor_feed_chkbox['state'] == 'disabled')
        self.assertTrue(self.settings_tab.keyword_search_chkbox['state'] == 'disabled')

        user_input_data = self.settings_tab.get_user_input_datas()
        self.assertEqual(user_input_data[4], 0)  # feed_blog_count
        self.assertIsNone(user_input_data[5])  # keyword
        self.assertEqual(user_input_data[6], 0)  # keyword_blog_count

if __name__ == '__main__':
    unittest.main()

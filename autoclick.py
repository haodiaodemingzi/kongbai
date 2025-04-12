import tkinter as tk
from tkinter import messagebox
# No longer need win32gui
import win32con
import win32api
import time
import threading

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.running = False
        self.setup_ui()
        
    def setup_ui(self):
        """初始化图形界面 (移除窗口相关)"""
        self.root.title("屏幕坐标自动点击器")
        self.root.geometry("350x250") # Adjusted size

        # 移除窗口标题输入和获取按钮
        # tk.Label(self.root, text="窗口标题:").grid(row=0, column=0, padx=5, pady=5)
        # self.window_title = tk.Entry(self.root, width=30)
        # self.window_title.grid(row=0, column=1, padx=5, pady=5)
        # self.btn_get = tk.Button(self.root, text="获取窗口", command=self.get_window)
        # self.btn_get.grid(row=0, column=2, padx=5, pady=5)

        # 坐标输入 (Adjusted row index)
        tk.Label(self.root, text="屏幕 X坐标:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.x_entry = tk.Entry(self.root, width=15)
        self.x_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.root, text="屏幕 Y坐标:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.y_entry = tk.Entry(self.root, width=15)
        self.y_entry.grid(row=1, column=1, padx=10, pady=10)

        # 点击间隔 (Adjusted row index)
        tk.Label(self.root, text="间隔(ms):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.interval = tk.Entry(self.root, width=15)
        self.interval.insert(0, "1000")
        self.interval.grid(row=2, column=1, padx=10, pady=10)

        # 控制按钮 (Adjusted row index)
        self.btn_start = tk.Button(self.root, text="开始点击", command=self.toggle, width=15)
        self.btn_start.grid(row=3, column=0, columnspan=2, pady=20)

        # 状态显示 (Adjusted row index)
        self.status = tk.Label(self.root, text="状态: 未运行", fg="gray")
        self.status.grid(row=4, column=0, columnspan=2)

    # Removed get_window method
    # def get_window(self):
    #     ...

    def toggle(self):
        """切换运行状态 (移除窗口句柄检查)"""
        # 移除窗口句柄检查
        # if not hasattr(self, 'hwnd') or self.hwnd == 0:
        #     messagebox.showwarning("警告", "请先获取窗口句柄")
        #     return
            
        self.running = not self.running
        if self.running:
            self.btn_start.config(text="停止点击")
            self.status.config(text="状态: 点击中...", fg="green")
            # Start the clicking thread
            self.click_thread = threading.Thread(target=self.run_clicker, daemon=True)
            self.click_thread.start()
        else:
            self.btn_start.config(text="开始点击")
            self.status.config(text="状态: 已停止", fg="red")
            # The thread will exit because self.running is False

    def run_clicker(self):
        """执行点击的线程 (使用绝对坐标)"""
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            interval_ms = int(self.interval.get())
            if interval_ms <= 0:
                messagebox.showwarning("警告", "点击间隔必须大于 0 ms")
                self.root.after(10, self.stop_from_thread) # Schedule stop in main thread
                return
            interval_sec = interval_ms / 1000.0
        except ValueError:
            messagebox.showerror("错误", "坐标和间隔必须输入有效数字")
            self.root.after(10, self.stop_from_thread) # Schedule stop in main thread
            return

        while self.running:
            # 移除窗口相关逻辑
            # rect = win32gui.GetWindowRect(self.hwnd)
            # abs_x = rect[0] + x
            # abs_y = rect[1] + y
            # win32gui.SetForegroundWindow(self.hwnd)
            # time.sleep(0.1) # Delay for window activation removed

            # 直接使用输入的x, y作为屏幕绝对坐标模拟点击
            try:
                win32api.SetCursorPos((x, y))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                time.sleep(0.05) # Brief pause between down and up
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                print(f"Clicked at ({x}, {y})") # Optional: print click info
            except Exception as e:
                # Handle potential errors during click (e.g., coordinate issues)
                print(f"Error during click: {e}")
                # Decide if you want to stop the clicker on error
                # self.root.after(10, self.stop_from_thread)
                # break # Exit the loop if click fails
                pass # Continue clicking even if one fails?

            # 等待指定间隔
            time.sleep(interval_sec)
            
        print("Clicker thread finished.")

    def stop_from_thread(self):
        """Helper method to safely stop the UI from the clicker thread"""
        if self.running:
            self.running = False
            self.btn_start.config(text="开始点击")
            self.status.config(text="状态: 出错停止", fg="orange")


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()

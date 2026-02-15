import pyautogui
import cv2
import numpy as np
import time

class ScreenCapture:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
    
    def capture_full_screen(self):
        """捕获全屏"""
        try:
            screenshot = pyautogui.screenshot()
            # 转换为OpenCV格式
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
        except Exception as e:
            print(f"捕获全屏失败: {e}")
            return None
    
    def capture_region(self, x, y, width, height):
        """捕获指定区域"""
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            # 转换为OpenCV格式
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
        except Exception as e:
            print(f"捕获区域失败: {e}")
            return None
    
    def capture_minecraft_window(self):
        """捕获Minecraft窗口"""
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle('Minecraft')
            if windows:
                window = windows[0]
                if window.isActive:
                    x, y, width, height = window.left, window.top, window.width, window.height
                    return self.capture_region(x, y, width, height)
        except ImportError:
            print("pygetwindow模块未安装")
        except Exception as e:
            print(f"捕获Minecraft窗口失败: {e}")
        return None
    
    def save_screenshot(self, frame, filename):
        """保存截图"""
        try:
            if frame is not None:
                cv2.imwrite(filename, frame)
                return True
        except Exception as e:
            print(f"保存截图失败: {e}")
        return False
    
    def show_screenshot(self, frame, title='Screenshot'):
        """显示截图"""
        try:
            if frame is not None:
                cv2.imshow(title, frame)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                return True
        except Exception as e:
            print(f"显示截图失败: {e}")
        return False
    
    def get_screen_size(self):
        """获取屏幕尺寸"""
        return self.screen_width, self.screen_height
    
    def capture_sequence(self, count=10, interval=0.5):
        """捕获序列截图"""
        screenshots = []
        for i in range(count):
            frame = self.capture_full_screen()
            if frame is not None:
                screenshots.append(frame)
            time.sleep(interval)
        return screenshots

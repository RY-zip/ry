import cv2
import numpy as np

class BlockDetector:
    def __init__(self):
        # 方块颜色阈值
        self.block_colors = {
            'grass': {'lower': np.array([35, 100, 100]), 'upper': np.array([85, 255, 255])},
            'dirt': {'lower': np.array([20, 100, 100]), 'upper': np.array([35, 255, 255])},
            'stone': {'lower': np.array([0, 0, 100]), 'upper': np.array([20, 50, 200])},
            'wood': {'lower': np.array([15, 100, 100]), 'upper': np.array([25, 255, 255])},
            'water': {'lower': np.array([85, 100, 100]), 'upper': np.array([135, 255, 255])}
        }
    
    def detect_blocks(self, frame):
        """检测图像中的方块"""
        if frame is None:
            return []
        
        # 转换为HSV颜色空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        detected_blocks = []
        
        # 检测每种类型的方块
        for block_type, color_range in self.block_colors.items():
            # 创建掩码
            mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 分析轮廓
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # 过滤小轮廓
                    # 获取边界框
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 计算中心点
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    detected_blocks.append({
                        'type': block_type,
                        'position': (center_x, center_y),
                        'bbox': (x, y, w, h),
                        'area': area
                    })
        
        return detected_blocks
    
    def draw_block_markers(self, frame, blocks):
        """在图像上绘制方块标记"""
        if frame is None:
            return None
        
        result = frame.copy()
        
        for block in blocks:
            x, y, w, h = block['bbox']
            block_type = block['type']
            center_x, center_y = block['position']
            
            # 绘制边界框
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 绘制中心点
            cv2.circle(result, (center_x, center_y), 5, (0, 0, 255), -1)
            
            # 绘制标签
            cv2.putText(result, block_type, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return result
    
    def get_block_at_position(self, frame, x, y):
        """获取指定位置的方块"""
        blocks = self.detect_blocks(frame)
        
        # 找到包含指定位置的方块
        for block in blocks:
            bx, by, bw, bh = block['bbox']
            if bx <= x <= bx + bw and by <= y <= by + bh:
                return block
        
        return None
    
    def detect_ground_blocks(self, frame):
        """检测地面方块"""
        if frame is None:
            return []
        
        height, width = frame.shape[:2]
        # 只检测图像下半部分
        ground_region = frame[height//2:, :]
        
        blocks = self.detect_blocks(ground_region)
        
        # 调整坐标
        for block in blocks:
            block['position'] = (block['position'][0], block['position'][1] + height//2)
            block['bbox'] = (block['bbox'][0], block['bbox'][1] + height//2, 
                           block['bbox'][2], block['bbox'][3])
        
        return blocks
    
    def detect_closest_block(self, frame):
        """检测最近的方块"""
        blocks = self.detect_blocks(frame)
        
        if not blocks:
            return None
        
        # 假设最近的方块面积最大
        closest_block = max(blocks, key=lambda b: b['area'])
        return closest_block

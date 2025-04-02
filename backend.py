import pandas as pd
from datetime import datetime, timedelta

class MaterialDateChecker:
    @staticmethod
    def convert_to_days(value, unit):
        """將不同時間單位轉換為天數"""
        try:
            value = float(value)
            if unit == '年':
                whole_years = int(value)
                partial_years = value - whole_years
                return int(whole_years * 365 + partial_years * 12 * 30)
            elif unit == '月':
                if value != int(value):
                    raise ValueError("月份必須為整數")
                return int(value * 30)
            elif unit == '週':
                if value != int(value):
                    raise ValueError("週數必須為整數")
                return int(value * 7)
            elif unit == '日':
                if value != int(value):
                    raise ValueError("天數必須為整數")
                return int(value)
            else:
                raise ValueError(f"不支援的單位: {unit}")
        except ValueError as e:
            raise ValueError(f"期限轉換錯誤: {str(e)}")
    
    @staticmethod
    def week_to_date_range(week_str):
        """將週代碼轉換為日期範圍"""
        try:
            year = int("20" + week_str[:2])
            week = int(week_str[2:])
            
            if week < 1 or week > 53:
                raise ValueError("週數必須在1-53之間")
                
            start_date = pd.to_datetime(f'{year}-W{week}-1', format='%Y-W%W-%w')
            end_date = start_date + pd.Timedelta(days=6)
            return start_date, end_date
        except ValueError as e:
            raise ValueError(f"無效的週別格式: {str(e)}")
    
    @staticmethod
    def parse_date_code(dc_code, format_type):
        """解析日期代碼"""
        try:
            if format_type == 'YYYYMMDD':
                return pd.to_datetime(dc_code, format='%Y%m%d')
            elif format_type == 'YYWW':
                start_date, _ = MaterialDateChecker.week_to_date_range(dc_code)
                return start_date
            else:
                raise ValueError("無效的日期格式")
        except Exception as e:
            raise ValueError(f"日期格式錯誤: {str(e)}")
    
    @staticmethod
    def convert_date_format(dc_code, format_type):
        """轉換日期格式並返回可讀的字符串"""
        try:
            if format_type == 'YYWW' and len(dc_code) == 4:
                start_date, end_date = MaterialDateChecker.week_to_date_range(dc_code)
                return {
                    'success': True,
                    'result': f"對應日期範圍: {start_date.strftime('%Y/%m/%d')} ~ {end_date.strftime('%Y/%m/%d')}"
                }
            elif format_type == 'YYYYMMDD' and len(dc_code) == 8:
                try:
                    date = pd.to_datetime(dc_code, format='%Y%m%d')
                    week_num = f"{str(date.year)[2:4]}{int(date.strftime('%V')):02d}"
                    return {
                        'success': True,
                        'result': f"對應週別: {week_num}"
                    }
                except Exception:
                    return {
                        'success': False,
                        'result': "格式錯誤"
                    }
            else:
                return {
                    'success': False,
                    'result': "格式錯誤"
                }
        except Exception as e:
            return {
                'success': False,
                'result': f"錯誤: {str(e)}"
            }
    
    @staticmethod
    def check_dates(data):
        """檢查日期並返回結果"""
        try:
            # 解析輸入數據
            part_no = data['partNo']
            dc_code = data['dcCode']
            format_type = data['dcFormat']
            iqc_limit_value = data['iqcLimit']
            iqc_unit = data['iqcUnit']
            storage_limit_value = data['storageLimit']
            storage_unit = data['storageUnit']
            
            # 基本驗證
            if not part_no:
                return {'error': True, 'message': "請輸入料號"}
            
            if not dc_code:
                return {'error': True, 'message': "請輸入來料DC"}
                
            if format_type == 'YYWW' and len(dc_code) != 4:
                return {'error': True, 'message': "YYWW格式必須為4位數字"}
                
            if format_type == 'YYYYMMDD' and len(dc_code) != 8:
                return {'error': True, 'message': "YYYYMMDD格式必須為8位數字"}
            
            if not iqc_limit_value:
                return {'error': True, 'message': "請輸入IQC檢驗期限"}
                
            if not storage_limit_value:
                return {'error': True, 'message': "請輸入總儲存期限"}
            
            # 轉換期限為天數
            try:
                iqc_limit = MaterialDateChecker.convert_to_days(iqc_limit_value, iqc_unit)
            except ValueError as e:
                return {'error': True, 'message': f"IQC檢驗期限錯誤: {str(e)}"}
            
            try:
                storage_limit = MaterialDateChecker.convert_to_days(storage_limit_value, storage_unit)
            except ValueError as e:
                return {'error': True, 'message': f"總儲存期限錯誤: {str(e)}"}
            
            # 解析日期代碼
            try:
                dc_date = MaterialDateChecker.parse_date_code(dc_code, format_type)
            except ValueError as e:
                return {'error': True, 'message': f"日期代碼錯誤: {str(e)}"}
            
            # 計算日期差異
            current_date = pd.Timestamp.now()
            days_since_dc = (current_date - dc_date).days
            storage_expiry_date = dc_date + pd.Timedelta(days=storage_limit)
            days_until_storage_expiry = (storage_expiry_date - current_date).days
            
            # 決定狀態
            iqc_status = days_since_dc <= iqc_limit
            storage_status = days_until_storage_expiry > 0
            
            # 生成結果文本
            if days_since_dc <= iqc_limit:
                result_text = (
                    f"料號:{part_no}，來料DC:{dc_code}，未超過IQC檢驗期限，"
                    f"距離總儲存期限還有{days_until_storage_expiry}天，"
                    f"到期日為:{storage_expiry_date.strftime('%Y-%m-%d')}"
                )
            elif days_since_dc > iqc_limit and days_until_storage_expiry > 0:
                result_text = (
                    f"料號:{part_no}，來料DC:{dc_code}，已超過IQC檢驗期限{days_since_dc - iqc_limit}天，"
                    f"距離總儲存期限還有{days_until_storage_expiry}天，"
                    f"到期日為:{storage_expiry_date.strftime('%Y-%m-%d')}"
                )
            else:
                result_text = (
                    f"料號:{part_no}，來料DC:{dc_code}，已超過總儲存期限{-days_until_storage_expiry}天，"
                    f"原到期日為:{storage_expiry_date.strftime('%Y-%m-%d')}"
                )
            
            return {
                'error': False,
                'iqc_status': iqc_status,
                'storage_status': storage_status,
                'result_text': result_text,
                'expiry_date': storage_expiry_date.strftime('%Y-%m-%d'),
                'days_until_expiry': days_until_storage_expiry
            }
            
        except Exception as e:
            return {
                'error': True,
                'message': f"檢查日期錯誤: {str(e)}"
            }
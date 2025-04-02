// DOM元素獲取
const dcCodeInput = document.getElementById('dcCode');
const dcFormatSelect = document.getElementById('dcFormat');
const convertedDateElem = document.getElementById('convertedDate');
const iqcStatusElem = document.getElementById('iqcStatus');
const storageStatusElem = document.getElementById('storageStatus');
const checkBtn = document.getElementById('checkBtn');
const copyBtn = document.getElementById('copyBtn');
const resultCard = document.getElementById('resultCard');
const resultText = document.getElementById('resultText');
const resultExpiry = document.getElementById('resultExpiry');
const toast = document.getElementById('toast');

// 事件監聽器設置
dcCodeInput.addEventListener('input', handleDcCodeChange);
dcFormatSelect.addEventListener('change', handleDcFormatChange);
checkBtn.addEventListener('click', checkDates);
copyBtn.addEventListener('click', copyResult);

// 函數定義
function handleDcCodeChange() {
    const dcCode = dcCodeInput.value.trim();
    const format = dcFormatSelect.value;
    
    if (!dcCode) {
        convertedDateElem.classList.remove('visible');
        return;
    }
    
    // 通過API獲取轉換結果
    window.pywebview.api.convert_date_code(dcCode, format)
        .then(response => {
            if (response.success) {
                convertedDateElem.textContent = response.result;
                convertedDateElem.classList.add('visible');
            } else {
                if (dcCode.length === (format === 'YYWW' ? 4 : 8)) {
                    convertedDateElem.textContent = response.result;
                    convertedDateElem.classList.add('visible');
                } else {
                    convertedDateElem.classList.remove('visible');
                }
            }
        })
        .catch(error => {
            console.error('轉換錯誤:', error);
            convertedDateElem.classList.remove('visible');
        });
}

function handleDcFormatChange() {
    dcCodeInput.value = '';
    convertedDateElem.classList.remove('visible');
}

function checkDates() {
    // 添加脈衝動畫
    checkBtn.classList.add('pulse');
    setTimeout(() => {
        checkBtn.classList.remove('pulse');
    }, 300);
    
    // 獲取所有輸入值
    const partNo = document.getElementById('partNo').value.trim();
    const dcCode = dcCodeInput.value.trim();
    const dcFormat = dcFormatSelect.value;
    const iqcLimit = document.getElementById('iqcLimit').value.trim();
    const iqcUnit = document.getElementById('iqcUnit').value;
    const storageLimit = document.getElementById('storageLimit').value.trim();
    const storageUnit = document.getElementById('storageUnit').value;
    
    // 基本驗證
    if (!partNo || !dcCode || !iqcLimit || !storageLimit) {
        showToast('請填寫所有必填欄位');
        return;
    }
    
    // 調用Python後端
    window.pywebview.api.check_dates({
        partNo: partNo,
        dcCode: dcCode,
        dcFormat: dcFormat,
        iqcLimit: iqcLimit,
        iqcUnit: iqcUnit,
        storageLimit: storageLimit,
        storageUnit: storageUnit
    }).then(result => {
        if (result.error) {
            showToast(result.message);
            return;
        }
        
        // 更新IQC狀態
        iqcStatusElem.classList.add('visible');
        if (result.iqc_status) {
            iqcStatusElem.classList.add('success');
            iqcStatusElem.classList.remove('danger');
            iqcStatusElem.textContent = '期限內';
        } else {
            iqcStatusElem.classList.add('danger');
            iqcStatusElem.classList.remove('success');
            iqcStatusElem.textContent = '!! 已超過 !!';
        }
        
        // 更新儲存狀態
        storageStatusElem.classList.add('visible');
        if (result.storage_status) {
            storageStatusElem.classList.add('success');
            storageStatusElem.classList.remove('danger');
            storageStatusElem.textContent = '期限內';
        } else {
            storageStatusElem.classList.add('danger');
            storageStatusElem.classList.remove('success');
            storageStatusElem.textContent = '!! 已超過 !!';
        }
        
        // 更新結果文本
        resultText.textContent = result.result_text;
        
        // 更新到期日
        resultExpiry.textContent = `到期日: ${result.expiry_date}`;
        if (result.days_until_expiry > 0) {
            resultExpiry.classList.add('success');
            resultExpiry.classList.remove('danger');
        } else {
            resultExpiry.classList.add('danger');
            resultExpiry.classList.remove('success');
        }
        
        // 顯示結果卡片
        resultCard.classList.add('visible');
    }).catch(error => {
        showToast('發生錯誤，請稍後再試');
        console.error('Error:', error);
    });
}

function copyResult() {
    const textToCopy = resultText.textContent.trim();
    
    if (textToCopy) {
        navigator.clipboard.writeText(textToCopy)
            .then(() => {
                copyBtn.classList.add('pulse');
                showToast('已複製到剪貼簿');
                setTimeout(() => {
                    copyBtn.classList.remove('pulse');
                }, 300);
            })
            .catch(() => {
                showToast('複製失敗，請手動選擇文本並複製');
            });
    } else {
        showToast('沒有可複製的內容');
    }
}

function showToast(message) {
    toast.querySelector('.toast-message').textContent = message;
    toast.classList.add('visible');
    
    setTimeout(() => {
        toast.classList.remove('visible');
    }, 3000);
}

// 確保圖標正確載入
document.addEventListener('DOMContentLoaded', function() {
    // 檢查頂部LOGO是否載入成功
    const topLogo = document.querySelector('.top-logo');
    topLogo.onerror = function() {
        console.error('頂部LOGO載入失敗');
        // 嘗試使用絕對路徑
        this.src = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/')) + '/CLA.ico';
    };
    
    // 檢查內聯LOGO是否載入成功
    const inlineLogo = document.querySelector('.inline-logo');
    inlineLogo.onerror = function() {
        console.error('內聯LOGO載入失敗');
        // 嘗試使用絕對路徑
        this.src = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/')) + '/CLA.ico';
    };
    
    // 隱藏初始元素
    convertedDateElem.classList.remove('visible');
    iqcStatusElem.classList.remove('visible');
    storageStatusElem.classList.remove('visible');
    resultCard.classList.remove('visible');
});
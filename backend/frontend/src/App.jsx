Enter// داخل دالة handleScan
const handleScan = async () => {
  setLoading(true);
  try {
    // استخدم العنوان النسبي أو عنوان التونل الخاص بك لاحقاً
    const apiUrl = process.env.REACT_APP_API_URL || '/api'; 
    
    const response = await fetch(`${apiUrl}/scan`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'x-token': 'cyber-admin-123' // 🔐 إرسال مفتاح الحماية
      },
      body: JSON.stringify({ target, scan_type: scanType, ai_model: model }),
    });
    // ... rest of the code
  } catch (error) { ... }
};

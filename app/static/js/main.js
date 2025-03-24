// 主JavaScript文件

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 自动关闭消息提示
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000); // 5秒后自动关闭
    });
    
    // 表格排序功能
    const tables = document.querySelectorAll('.table-sortable');
    tables.forEach(function(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function(header) {
            header.classList.add('sortable');
            header.addEventListener('click', function() {
                const column = this.getAttribute('data-sort');
                const order = this.classList.contains('asc') ? 'desc' : 'asc';
                
                // 重置所有标题样式
                headers.forEach(h => {
                    h.classList.remove('asc', 'desc');
                });
                
                // 设置当前列的排序方向
                this.classList.add(order);
                
                // 排序表格
                sortTable(table, column, order);
            });
        });
    });
});

// 表格排序函数
function sortTable(table, column, order) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // 排序行
    rows.sort((a, b) => {
        const cellA = a.querySelector(`td:nth-child(${parseInt(column) + 1})`).textContent.trim();
        const cellB = b.querySelector(`td:nth-child(${parseInt(column) + 1})`).textContent.trim();
        
        // 检查是否为数字
        const isNumeric = !isNaN(cellA) && !isNaN(cellB);
        
        if (isNumeric) {
            return order === 'asc' 
                ? parseFloat(cellA) - parseFloat(cellB)
                : parseFloat(cellB) - parseFloat(cellA);
        } else {
            return order === 'asc'
                ? cellA.localeCompare(cellB)
                : cellB.localeCompare(cellA);
        }
    });
    
    // 重新添加排序后的行
    rows.forEach(row => tbody.appendChild(row));
} 
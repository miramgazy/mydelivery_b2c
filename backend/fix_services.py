import re

file_path = '/Users/miramgazy/Library/Mobile Documents/com~apple~CloudDocs/Progects/tg-delivery/backend/apps/orders/services.py'
with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
in_send_to_iiko = False
in_get_order_status = False

for line in lines:
    if 'def send_to_iiko' in line:
        in_send_to_iiko = True
        new_lines.append(line)
        continue
    if in_send_to_iiko:
        if 'def _prepare_iiko_order_data' in line:
            in_send_to_iiko = False
        else:
            # Fix indentation for lines that look like they belong to a block
            if 'order.iiko_order_id =' in line or 'order.order_number =' in line or 'order.status =' in line or 'order.sent_to_iiko_at =' in line or 'order.iiko_response =' in line or 'order.error_message =' in line or 'order.save(' in line or 'logger.info(' in line or 'return True' in line:
                new_lines.append('                ' + line.lstrip())
                continue
            
    if 'def get_order_status' in line:
        in_get_order_status = True
        new_lines.append(line)
        continue
    if in_get_order_status:
        if 'return status_data' in line:
             new_lines.append('                ' + line.lstrip())
             in_get_order_status = False
             continue

    new_lines.append(line)

# Let's try a simpler approach - just replace the whole file with a clean version since I have it.

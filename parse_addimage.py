import re
import uuid
import json


def parse_and_replace_addimage(js_code):
    """
    解析JS脚本代码，使用UUID替换所有slide.addImage的path参数
    返回替换后的完整脚本和所有替换后的slide.addImage参数
    
    Args:
        js_code: JS脚本代码字符串
    """
    content = js_code
    
    # 存储所有替换信息
    replacements = []
    
    # 匹配 slide.addImage({ ... }) 的正则表达式
    # 使用非贪婪匹配来找到完整的addImage调用
    addimage_pattern = r'(slide\.addImage\s*\(\s*\{)([\s\S]*?)(\}\s*\))'
    
    def replace_path(match):
        prefix = match.group(1)  # slide.addImage({
        params_content = match.group(2)  # 参数内容
        suffix = match.group(3)  # })
        
        # 生成新的UUID
        new_uuid = str(uuid.uuid4())
        
        # 匹配path参数（支持单引号、双引号和空字符串）
        path_pattern = r'(path\s*:\s*)(["\'])([^"\']*?)(\2)'
        
        # 提取原始path值
        path_match = re.search(path_pattern, params_content)
        original_path = path_match.group(3) if path_match else ""
        
        # 替换path值为UUID
        new_params_content = re.sub(
            path_pattern,
            rf'\g<1>\g<2>{new_uuid}\g<4>',
            params_content
        )
        
        # 提取完整的addImage参数对象
        full_params = prefix + new_params_content + suffix
        
        # 解析参数为字典格式
        param_dict = extract_params_to_dict(new_params_content, new_uuid)
        param_dict['original_path'] = original_path
        param_dict['new_path'] = new_uuid
        
        replacements.append(param_dict)
        
        return prefix + new_params_content + suffix
    
    # 执行替换
    new_content = re.sub(addimage_pattern, replace_path, content)
    
    return new_content, replacements


def extract_params_to_dict(params_str, new_uuid):
    """
    从参数字符串中提取参数为字典格式
    """
    result = {}
    
    # 提取path
    path_match = re.search(r'path\s*:\s*["\']([^"\']*)["\']', params_str)
    if path_match:
        result['path'] = path_match.group(1)
    
    # 提取x
    x_match = re.search(r'x\s*:\s*([\d.]+)', params_str)
    if x_match:
        result['x'] = float(x_match.group(1))
    
    # 提取y
    y_match = re.search(r'y\s*:\s*([\d.]+)', params_str)
    if y_match:
        result['y'] = float(y_match.group(1))
    
    # 提取w
    w_match = re.search(r'w\s*:\s*([\d.]+)', params_str)
    if w_match:
        result['w'] = float(w_match.group(1))
    
    # 提取h
    h_match = re.search(r'h\s*:\s*([\d.]+)', params_str)
    if h_match:
        result['h'] = float(h_match.group(1))
    
    # 提取sizing
    sizing_match = re.search(r'sizing\s*:\s*\{\s*type\s*:\s*["\']([^"\']*)["\']', params_str)
    if sizing_match:
        result['sizing'] = {'type': sizing_match.group(1)}
    
    # 提取altText
    alttext_match = re.search(r'altText\s*:\s*["\']([^"\']*)["\']', params_str)
    if alttext_match:
        result['altText'] = alttext_match.group(1)
    
    return result


def main():
    js_file = 'test.js'
    
    # 读取JS代码
    with open(js_file, 'r', encoding='utf-8') as f:
        js_code = f.read()
    
    # 解析并替换
    new_content, replacements = parse_and_replace_addimage(js_code)
    
    # 构建返回结果
    result = {
        "replaced_script": new_content,
        "addimage_params": replacements
    }
    
    # 输出JSON结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return result


if __name__ == '__main__':
    main()

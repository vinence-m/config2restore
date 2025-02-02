import os
import shutil
import argparse
import glob
import json
import orjson


def decode_uuid(enc_uuid):
    i = [64] * 43 + [62] + [64] * 3 + [63] + [k for k in range(52,62)] + \
        [64] * 7 + [j for j in range(26)] + [64] * 6 + [l for l in range(26,52)]
    a = [""] * 8 + (["-"] + [""] * 4) * 3 + ["-"] + [""] * 12
    n = '0123456789abcdef'
    s = [i for i in range(36) if i not in {8, 13, 18, 23}]
    r = 2
    if len(enc_uuid) != 22:
        return enc_uuid
    a[0] = enc_uuid[0]
    a[1] = enc_uuid[1]
    for idx in range(2, 22, 2):
        o = i[ord(enc_uuid[idx])]
        l = i[ord(enc_uuid[idx + 1])]
        a[s[r]] = n[o >> 2]
        a[s[r + 1]] = n[(3 & o) << 2 | l >> 4]
        a[s[r + 2]] = n[15 & l]
        r += 3
    return ''.join(a)

def get_path(path_dict, EXT_dir):
    PATHS = {}
    for k, v in path_dict.items():
        temp = v[0].strip()
        a = f"{EXT_dir}/{temp}"
        PATHS.update({int(k):a})
    return PATHS


def success_match(src_FILE, new_dir, processfile):
    dst_file = os.path.join(new_dir, processfile)
    os.makedirs(new_dir, exist_ok=True)  
    counter = 1
    if os.path.exists(dst_file):
        name, ext = os.path.splitext(processfile)
        new_file = f"{name}_{counter}{ext}"
        dst_file = os.path.join(new_dir, new_file)
        counter += 1
    print(f"复制文件: {src_FILE} -> {dst_file}")
    shutil.copy(src_FILE, dst_file)


def copy_file(src_base, verD, decuuids, Paths, ExT_dir):
    vercheck = []
    overidxfilesset = set()
    for root, dirs, files in os.walk(src_base):
        for file in files:
            splitname = file.split('.')
            uuid = splitname[0]
            src_file = os.path.join(root, file)
            try:
                if uuid in decuuids:
                    path_idx = decuuids.index(uuid)
                    output_dir = Paths.get(path_idx)
                    if spinedec_only and (spine_sig not in output_dir):
                        continue
                    success_match(src_file, output_dir, file)
                else:
                    # uuid是文件夹时
                    foldername = os.path.basename(root)
                    fosplit = foldername.split('.')
                    fouuid = fosplit[0]
                    if fouuid in decuuids:
                        path_idx = decuuids.index(fouuid)
                        output_dir = Paths.get(path_idx)
                        if spinedec_only and (spine_sig not in output_dir):
                            continue
                        success_match(src_file, output_dir, file)
                    else:
                        if spinedec_only:
                            continue
                        failure_dir = f'failure\\{root}'
                        os.makedirs(failure_dir, exist_ok=True)
                        dst_file = os.path.join(failure_dir, file)
                        print(f"失败文件: {src_file} -> {dst_file}")
                        shutil.copy(src_file, failure_dir)
            except:
                try:
                    # uuid定位不到path时，通过ver辅助定位path
                    if uuid in decuuids:
                        uid_idx = decuuids.index(uuid)
                        vername = splitname[1]
                        if vername not in vercheck: 
                            vercheck.append(vername)
                            basever_idx = verD[src_base][vername-1]
                            output_dir = Paths.get(basever_idx)
                            if spinedec_only and (spine_sig not in output_dir):
                                continue
                            success_match(src_file, output_dir, file)
                            continue
                        else:
                            raise Exception(f'{vername} exist:File:{file}')
                except:
                    info = (root, file)
                    overidxfilesset.add(info)
                    continue
    return overidxfilesset


def overrangge_file(overlist, EXT_dir):
    unknown_list = []
    for row in overlist:
        over_file = os.path.join(row[0], row[1])
        if spinedec_only and (spine_sig not in over_file):
            continue
        try:
            with open(over_file, 'r', encoding='utf-8') as f:
                tdata = f.read()
            tjson = orjson.loads(tdata)
            enc_link_uuid = tjson[1][0]
            dec_link_uuid = decode_uuid(enc_link_uuid)
            for root, dirs, files in os.walk(EXT_dir):
                for file in files:
                    splitname = file.split('.')
                    uuid = splitname[0]
                    # json中的uuid链接定位path
                    if dec_link_uuid == uuid:
                        link_dir = os.path.join(root, row[1])
                        print(f"复制链接文件: {over_file} -> {link_dir}")
                        shutil.copy(over_file, link_dir)
                        break
                else:
                    continue
                break
            else:
                if spinedec_only:
                    continue
                overidx_dir = f'failure\\{row[0]}'
                os.makedirs(overidx_dir, exist_ok=True)
                dst_file = os.path.join(overidx_dir, row[1])
                unknown_list.extend([overidx_dir, row[1]])
                print(f"超索引文件: {over_file} -> {dst_file}")
                shutil.copy(over_file, dst_file)
        except Exception:
            if spinedec_only:
                continue
            overlink_dir = f'failure\\{row[0]}'
            os.makedirs(overlink_dir, exist_ok=True)
            dst_file = os.path.join(overlink_dir, row[1])
            unknown_list.extend([overlink_dir, row[1]])
            print(f"超链接文件: {over_file} -> {dst_file}")
            shutil.copy(over_file, dst_file)
            continue
    return unknown_list


def spine_json(out_dir):
    for root, dirs, files in os.walk(out_dir):
        flag = False
        filec = [f'{root}\\{f}' for f in files if (os.path.isfile(f'{root}\\{f}') and f.endswith('.json'))]
        pngs = [f for f in files if (os.path.isfile(f'{root}\\{f}') and f.endswith('.png'))]
        atlas0 = [f for f in files if (os.path.isfile(f'{root}\\{f}') and f.endswith('.atlas'))]
        bins = [f for f in files if (os.path.isfile(f'{root}\\{f}') and f.endswith('.bin'))]
        filec.sort(key=lambda x: os.path.getsize(x),reverse=True)
        while filec:
            m_json = filec.pop(0)
            try:
                with open(m_json, 'r', encoding='utf-8') as f:
                    datax = f.read()
                jsondatax = orjson.loads(datax)
                if jsondatax[3][0][0] == 'sp.SkeletonData':
                    spine_data = jsondatax[5][0]
                    spine_name = spine_data[1]
                    #spine_name = os.path.basename(root)
                    print(f'正在写入{spine_name}')
                    if isinstance(spine_data[4], dict):
                        try:
                            skel_data = orjson.dumps(spine_data[4], option=orjson.OPT_INDENT_2)
                            with open(os.path.join(root, f'{spine_name}.skel.json'), 'wb') as f:
                                f.write(skel_data)
                        except Exception as e:
                            print(f"写入文件时出错: {e}")
                        atlas_data = spine_data[2].replace('\\n', '\n')
                        with open(os.path.join(root, f'{spine_name}.atlas'), 'w', encoding='utf-8') as f:
                            f.write(atlas_data)
                        pngslength = len(pngs)
                        for n, p in enumerate(pngs):
                            if pngslength == 1:
                                os.rename(f'{root}\\{p}', f'{root}\\{spine_name}.png')
                            else:
                                os.rename(f'{root}\\{p}', f'{root}\\{spine_name}_{n+1}.png')
                    else:
                        atlas_data = spine_data[3].replace('\\n', '\n')
                        with open(os.path.join(root, f'{spine_name}.atlas'), 'w', encoding='utf-8') as f:
                            f.write(atlas_data)
                        pngslength = len(pngs)
                        for n, p in enumerate(pngs):
                            if pngslength == 1:
                                os.rename(f'{root}\\{p}', f'{root}\\{spine_name}.png')
                            else:
                                os.rename(f'{root}\\{p}', f'{root}\\{spine_name}_{n+1}.png')
                        binslength = len(bins)
                        if binslength == 1:
                            os.rename(f'{root}\\{bins[0]}', f'{root}\\{spine_name}.skel')
                        else:
                            print(f'bin文件异常, {bins}')
                    flag = True
                    break
                else:
                    continue
            except Exception as e:
                print(f'错误: {e}')
        if flag:
            del dirs[:]

def main():
    global spinedec_only
    global spine_sig
    
    parser = argparse.ArgumentParser(description="Cocos2d Restore and decrypt spine.")
    parser.add_argument("-s", action='store_true', help="Optional: Only decrypt spine or not")
    parser.add_argument("-n", help="Optional: Specify the spine folder name or other")
    args = parser.parse_args()
    
    spine_sig = 'Spine'
    spinedec_only = args.s
    if args.s:
        spine_sig = args.n
    ext_dir = 'output'
    if spinedec_only:
        print('正在查找Spine文件...')
    
    pattern = os.path.join(os.getcwd(), "*config*.json")
    config_file = glob.glob(pattern)
    with open(config_file[0], 'r', encoding='utf-8') as f:
        data = f.read()
    jsondata = orjson.loads(data)
    uuids = jsondata['uuids']
    dec_uuids = [decode_uuid(uuid) for uuid in uuids]
    paths = get_path(jsondata['paths'], ext_dir)
    base_name = [jsondata['importBase'], jsondata['nativeBase']]
    basever_dl = jsondata['versions']
    catch_overset = set()
    for base in base_name:
        result = copy_file(base, basever_dl, dec_uuids, paths, ext_dir)
        catch_overset.update(result)
    catch_overlist = [list(i) for i in catch_overset]
    ukl = overrangge_file(catch_overlist, ext_dir)
    if ukl:
        with open('unknowfile.txt','w',encoding='utf-8') as f:
            for item in ukl:
                f.write(f"{item}\n")
    spine_json(ext_dir)
    print('finish')


if __name__ == '__main__':
    main()

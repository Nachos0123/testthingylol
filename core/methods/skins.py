import concurrent.futures
from core.Structures.EpicData import EpicData
from core.constants   import affilaiteCode

from core.rarity.priority import mythic_ids, rarity_priority, sub_order
from core.rarity.v1       import rarities

import aiohttp, platform, json, asyncio, re, os, concurrent, io, datetime, math

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

# 1720 start of skin checker loop
# 466  sort_ids_by_rarity function
# 369  get_cosmetic_info  function
# 436  get_cosmetic_type  function
# 1049 createimg          function

order = ["Banners", "Skins", "Back Blings", "Pickaxes", "Emotes", "Gliders", "Wraps", "Sprays", "Emojis", "Other"]
idpattern = re.compile(r"athena(.*?):(.*?)_(.*?)")
FONT_PATH = './core/images/fonts/font.tff'

class skins:
    def __init__(self) -> None:
        self.userAgent = f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"

    async def get(self, user: 'EpicData') -> dict:

        async with aiohttp.ClientSession(headers={"User-Agent": self.userAgent}) as session:

            async with session.request(
                method="POST",
                url=f"https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{user.accountID}/client/QueryProfile?profileId=athena",
                headers={
                    "Authorization": f"Bearer {user.accessToken}",
                    "content-type": "application/json"
                },
                json={}
            ) as response:

                if response.status != 200:
                    return False
                
                profile = await response.json()

        locker_data = {'unlocked_styles': {}}
        athena_data = profile

        for item_id, item_data in athena_data['profileChanges'][0]['profile']['items'].items():

            template_id:str = item_data.get('templateId', '')
            if template_id.startswith('Athena'):

                lowercase_cosmetic_id = template_id.split(':')[1]
                if lowercase_cosmetic_id not in locker_data['unlocked_styles']:
                    locker_data['unlocked_styles'][lowercase_cosmetic_id] = []

                attributes = item_data.get('attributes', {})
                variants   = item_data.get('variants', [])

                for variant in variants:
                    locker_data['unlocked_styles'][lowercase_cosmetic_id].extend(variant.get('owned', []))

        exclusive_cosmetics = [
            'CID_017_ATHENA_COMMANDO_M',
            'CID_028_ATHENA_COMMANDO_F',
            'CID_029_ATHENA_COMMANDO_F_HALLOWEEN',
            'CID_030_ATHENA_COMMANDO_M_HALLOWEEN',
            'CID_116_ATHENA_COMMANDO_M_CARBIDEBLACK',
            'CID_315_ATHENA_COMMANDO_M_TERIYAKIFISH',
        ]

        items = {}
        for it_data in profile['profileChanges'][0]['profile']['items'].values():

            tid = it_data['templateId'].lower()
            if idpattern.match(tid):

                item_type = get_cosmetic_type(tid)
                if item_type not in items:

                    items[item_type] = []

                items[item_type].append(tid.split(':')[1])

        for group in order:

            if group in items:
                sorted_ids = await sort_ids_by_rarity(items[group], item_order=order)
                image_data = await createimg(
                    sorted_ids,
                    session,
                    username='lmaohi',
                    sort_by_rarity=True,
                    item_order=order,
                    locker_data=locker_data,
                    exclusive_cosmetics=exclusive_cosmetics
                )

                if image_data:
                    return image_data


async def download_cosmetic_images(ids:list):

        userAgent = f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"
        async with aiohttp.ClientSession(headers={"User-Agent": userAgent}) as session:

            async def _dl(id: str):
                imgpath = f"./core/cache/{id}.png"
                if not os.path.exists(imgpath) or not os.path.isfile(imgpath) or os.path.getsize(imgpath) == 0:

                    urls = [
                        f"https://fortnite-api.com/images/cosmetics/br/{id}/icon.png",
                        f"https://fortnite-api.com/images/cosmetics/br/{id}/smallicon.png"
                    ]

                    for url in urls:
                        async with session.get(url) as response:

                            if response.status == 200:
                                content = await response.read()

                                with open(imgpath, "wb") as f:
                                    f.write(content)
                                
                                return
                            
                    else:
                        with open(imgpath, "wb") as f:
                            f.write(open("./core/cache/tbd.png", "rb").read())

            await asyncio.gather(*[_dl(id) for id in ids])

converted_mythic_ids = []

async def createimg(
        ids: list, title: str=None, username: str = "User", sort_by_rarity: bool=False, show_fake_text: bool=False, item_order: list=None,
        locker_data=None, exclusive_cosmetics=None, user_id: int=None
    ):

    if not os.path.exists("./core/cache"):
        os.makedirs("./core/cache")
    
    await download_cosmetic_images(ids)

    rarity_version = "v1"
    custom_link    = "discord.gg/heals"

    backgrounds_to_use = rarities.rarity_backgroundsV1
    logo_path          = "./core/cache/medkit.png"
    logo_filename       = logo_path if os.path.exists(logo_path) else os.path.join("./core/cache", "tbd.jpg")

    cosmetic_info_tasks = [get_cosmetic_info(cid) for cid in ids]
    results = await asyncio.gather(*cosmetic_info_tasks)

    info_list = []
    for cosmetic_found in results:

        if cosmetic_found['name'].strip().lower() == "unknown":
            continue

        cid_lower = cosmetic_found['id'].lower()
        make_mythic = False

        if exclusive_cosmetics and locker_data:
            if cosmetic_found['id'].upper() in exclusive_cosmetics:

                if cid_lower == 'cid_028_athena_commando_f':
                    if 'Mat3' in locker_data['unlocked_styles'].get('cid_028_athena_commando_f', []):

                        make_mythic = True
                        cosmetic_found['name'] = 'OG Renegade Raider'
                    
                    else:

                        make_mythic = False
                        cosmetic_found['name']  = 'Renegade Raider'

                if cid_lower in mythic_ids:
                    make_mythic = False

        if cid_lower in mythic_ids:
            make_mythic = False

        if make_mythic:
            cosmetic_found['rarity'] = 'Mythic'
            converted_mythic_ids.append(cosmetic_found['id'])

        info_list.append(cosmetic_found)

    if not info_list:
        return None
    
    def find_substitute_url(cosmetic, locker_data):
        substituion_map = {
            'cid_017_athena_commando_m': {'mat3': './core/images/style/Renegade.png'}
        }

        cid_lower = cosmetic['id'].lower()
        if not locker_data:
            return None
        
        if cid_lower not in substituion_map:
            return None
        
        styles = locker_data.get('unlocked_styles', {}).get(cosmetic['id'], [])
        for style in styles:
            style_lower = style.lower()
            if style_lower in substituion_map[cid_lower]:
                return substituion_map[cid_lower][style_lower]
            
        return None
    
    work_args_list = []
    for cosmetic in info_list:

        rarity = cosmetic.get('rarity', 'Common')
        backgrounds_path = backgrounds_to_use.get(rarity, backgrounds_to_use['Common'])
        sub_url = find_substitute_url(cosmetic, locker_data)

        work_args = {
            'cid': cosmetic['id'],
            'name': cosmetic['name'],
            'rarity': rarity,
            'background_path': backgrounds_path,
            'substitute_image_url': sub_url
        }
        work_args_list.append(work_args)

    images = [] # 1225
    if work_args_list:
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            for final_img in executor.map(_process_cosmetic_item, work_args_list):
                images.append(final_img)

    if images:
        if sort_by_rarity:
            sorted_pairs = sorted(
                zip(info_list, images),
                key=lambda x: rarity_priority.get(x[0]["rarity"], 999)
            )
            sorted_images = [img for _, img in sorted_pairs]
        elif item_order:
            sorted_pairs = sorted(
                zip(info_list, images),
                key=lambda x: item_order.index(get_cosmetic_type(x[0]["id"]))
                    if get_cosmetic_type(x[0]["id"]) in item_order
                    else len(item_order)
            )
            sorted_images = [img for _, img in sorted_pairs]
        else:
            sorted_images = images

        combined_image = combine_images(
            sorted_images, 
            username, 
            len(info_list),
            logo_filename=logo_filename, 
            show_fake_text=show_fake_text, 
            custom_link=custom_link
        )

        f = io.BytesIO()
        combined_image.save(f, "PNG")
        f.seek(0)
        return f
    else:
        return None
    
def combine_images(
    images,
    username: str,
    item_count: int,
    logo_filename="./core/cache/medkit.png",
    show_fake_text: bool = False,
    custom_link: str = "t.me/medkit"
):
    max_width = 1848
    max_height = 2048

    num_items = len(images)
    base_max_cols = 6
    max_cols = base_max_cols
    num_rows = math.ceil(num_items / max_cols)

    while num_rows > max_cols:
        max_cols += 1
        num_rows = math.ceil(num_items / max_cols)

    item_width = max_width // max_cols
    item_height = max_height // num_rows
    image_size = min(item_width, item_height)
    spacing = 0 

    total_width = max_cols * image_size + (max_cols - 1) * spacing
    total_height = num_rows * image_size + (num_rows - 1) * spacing
    empty_space_height = image_size
    total_height += empty_space_height

    combined_image = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 255))

    for idx, image in enumerate(images):
        col = idx % max_cols
        row = idx // max_cols
        position = (col * (image_size + spacing), row * (image_size + spacing))
        resized_image = image.resize((image_size, image_size), Image.Resampling.LANCZOS)
        combined_image.paste(resized_image, position, resized_image)
    try:
        logo = Image.open(logo_filename).convert("RGBA")
    except FileNotFoundError:
        logo = Image.new("RGBA", (100, 100), (255, 255, 255, 255))

    logo_height = int(empty_space_height * 0.6)
    logo_width = int((logo_height / logo.height) * logo.width)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

    logo_position = (
        10,
        total_height - empty_space_height + (empty_space_height - logo_height) // 2 
    )
    combined_image.paste(logo, logo_position, logo)

    text1 = f"Total: {item_count}"
    text2 = f"@{username} / {datetime.now().strftime('%d/%m/%y')}"
    text3 = custom_link
    max_text_width = total_width - (logo_position[0] + logo_width + 20)
    font_size = logo_height // 3

    try:
        font = ImageFont.truetype(FONT_PATH, size=font_size)
    except IOError:
        font = ImageFont.load_default()

    text_bbox1 = font.getbbox(text1)
    text_bbox2 = font.getbbox(text2)
    text_bbox3 = font.getbbox(text3)
    text_width1, text_height1 = text_bbox1[2] - text_bbox1[0], text_bbox1[3] - text_bbox1[1]
    text_width2, text_height2 = text_bbox2[2] - text_bbox2[0], text_bbox2[3] - text_bbox2[1]
    text_width3, text_height3 = text_bbox3[2] - text_bbox3[0], text_bbox3[3] - text_bbox3[1]

    while (
        (text_width1 > max_text_width or text_width2 > max_text_width or text_width3 > max_text_width)
        and font_size > 8
    ):
        font_size -= 1
        try:
            font = ImageFont.truetype(FONT_PATH, size=font_size)
        except IOError:
            font = ImageFont.load_default()
            break
        text_bbox1 = font.getbbox(text1)
        text_bbox2 = font.getbbox(text2)
        text_bbox3 = font.getbbox(text3)
        text_width1, text_height1 = text_bbox1[2] - text_bbox1[0], text_bbox1[3] - text_bbox1[1]
        text_width2, text_height2 = text_bbox2[2] - text_bbox2[0], text_bbox2[3] - text_bbox2[1]
        text_width3, text_height3 = text_bbox3[2] - text_bbox3[0], text_bbox3[3] - text_bbox3[1]

    total_text_height = text_height1 + text_height2 + text_height3 + 10
    text_y_start = total_height - empty_space_height + (empty_space_height - total_text_height) // 2

    text_x = logo_position[0] + logo_width + 10
    text_y1 = text_y_start
    text_y2 = text_y1 + text_height1 + 5
    text_y3 = text_y2 + text_height2 + 5

    draw = ImageDraw.Draw(combined_image)
    draw.text((text_x, text_y1), text1, fill="white", font=font)
    draw.text((text_x, text_y2), text2, fill="white", font=font)
    draw.text((text_x, text_y3), text3, fill="white", font=font)

    return combined_image

def _process_cosmetic_item(args):

    cid              = args["cid"]
    name             = args["name"]
    rarity           = args["rarity"]
    background_path  = args["background_path"]
    substitute_url   = args.get("substitute_image_url")

    imgpath = f'./core/cache/{cid}.png' # 1013

    try:
        if substitute_url:
            if substitute_url.startswith("http"):
                img = Image.open("./core/cache/tbd.png").convert("RGBA")
            else:
                img = Image.open(substitute_url).convert("RGBA")
        else:
            img = Image.open(imgpath).convert("RGBA")

        if img.size == (1, 1):
            raise IOError("1x1 image (placeholder).")
    except (UnidentifiedImageError, IOError) as e:
        img = Image.open("./core/cache/tbd.png").convert("RGBA")

    try:
        background = Image.open(background_path)
    except (UnidentifiedImageError, IOError) as e:
        background = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    final_img = combine_with_background(img, background, name, rarity)

    return final_img

def combine_with_background(foreground: Image.Image, background: Image.Image, name: str, rarity: str) -> Image.Image:
    
    bg = background.convert('RGBA')
    fg = foreground.convert('RGBA')

    fg = fg.resize(bg.size, Image.Resampling.LANCZOS)
    bg.paste(fg, (0, 0), fg)
    draw = ImageDraw.Draw(bg)

    special_rarities = {
        "ICON SERIES", "DARK SERIES", "STAR WARS SERIES", "GAMING LEGENDS SERIES",
        "MARVEL SERIES", "DC SERIES", "SHADOW SERIES", "SLURP SERIES", "LAVA SERIES", "FROZEN SERIES"
    }

    base_max_font_size = 40 # 584

    if rarity.upper() in special_rarities:
        max_font_size = calculate_font_size_for_special(name, base_size=base_max_font_size)
    else:
        max_font_size = base_max_font_size

    min_font_size = 10
    max_text_width = bg.width - 20
    font_size = max_font_size

    name = name.upper()
    while font_size > min_font_size:
        try:
            font = ImageFont.truetype(FONT_PATH, size=font_size)
        except IOError:
            return bg

        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]

        if text_width <= max_text_width:
            break

        font_size -= 1

    try:
        font = ImageFont.truetype(FONT_PATH, size=font_size)
    except IOError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (bg.width - text_width) // 2

    muro_y_position = int(bg.height * 0.80)
    muro_height = bg.height - muro_y_position

    muro = Image.new('RGBA', (bg.width, muro_height), (0, 0, 0, int(255 * 0.7)))
    bg.paste(muro, (0, muro_y_position), muro)

    text_y = muro_y_position + (muro_height - text_height) // 2

    draw.text((text_x, text_y), name, fill="white", font=font)

    return bg

def calculate_font_size_for_special(name: str, base_size: int = 40) -> int:
    length = len(name)
    if length <= 1:
        return int(base_size * 1)
    elif length <= 2:
        return int(base_size * 2)
    elif length <= 3:
        return int(base_size * 2)
    elif length <= 4:
        return int(base_size * 2)
    elif length <= 5:
        return int(base_size * 2)
    elif length <= 6:
        return int(base_size * 2)
    elif length <= 7:
        return int(base_size * 2)
    elif length <= 8:
        return int(base_size * 2)
    elif length <= 9:
        return int(base_size * 2)
    elif length <= 10:
        return int(base_size * 2)
    elif length <= 11:
        return int(base_size * 3)
    elif length <= 12:
        return int(base_size * 3)
    elif length <= 13:
        return int(base_size * 3)
    elif length <= 14:
        return int(base_size * 3)
    elif length <= 15:
        return int(base_size * 3)
    else:
        return int(base_size * 3)

def calculate_font_size(name: str, base_size: int = 40, special: bool = False) -> int:
    if special:
        length = len(name)
        if length <= 1:
            return int(base_size * 0.4)
        elif length <= 2:
            return int(base_size * 0.5)
        elif length <= 3:
            return int(base_size * 0.6)
        elif length <= 4:
            return int(base_size * 0.7)
        elif length <= 5:
            return int(base_size * 0.8)
        elif length <= 6:
            return int(base_size * 0.9)
        elif length <= 7:
            return int(base_size * 1.0)
        elif length <= 8:
            return int(base_size * 1.1)
        elif length <= 9:
            return int(base_size * 1.2)
        elif length <= 10:
            return int(base_size * 1.3)
        elif length <= 11:
            return int(base_size * 1.4)
        elif length <= 12:
            return int(base_size * 1.5)
        elif length <= 13:
            return int(base_size * 1.6)
        elif length <= 14:
            return int(base_size * 1.7)
        elif length <= 15:
            return int(base_size * 1.8)
        else:
            return int(base_size * 2.0)
    else:
        return base_size


def get_cosmetic_type(cosmetic_id):
    if "character_" in cosmetic_id or "cid" in cosmetic_id:
        return "Skins"
    elif "bid_" in cosmetic_id or "backpack" in cosmetic_id:
        return "Back Blings"
    elif (
        "pickaxe_" in cosmetic_id or "pickaxe_id_" in cosmetic_id or 
        "DefaultPickaxe" in cosmetic_id or "HalloweenScythe" in cosmetic_id or
        "HappyPickaxe" in cosmetic_id or "SickleBatPickaxe" in cosmetic_id or
        "SkiIcePickaxe" in cosmetic_id or "SpikyPickaxe" in cosmetic_id
    ):
        return "Pickaxes"
    elif "eid" in cosmetic_id or "emote" in cosmetic_id:
        return "Emotes"
    elif (
        "glider" in cosmetic_id or
        "founderumbrella" in cosmetic_id or
        "founderglider" in cosmetic_id or
        "solo_umbrella" in cosmetic_id
    ):
        return "Gliders"
    elif "wrap" in cosmetic_id:
        return "Wraps"
    elif "spray" in cosmetic_id:
        return "Sprays"
    elif "emoji" in cosmetic_id:
        return "Emojis"
    else:
        return "Others"

async def sort_ids_by_rarity(ids: list, item_order:list) -> list:
    cosmetic_info_tasks = [get_cosmetic_info(id) for id in ids]
    info_list = await asyncio.gather(*cosmetic_info_tasks)

    def get_sort_key(info):
        # Info
        rarity        = info.get("rarity", "Uknown")
        cosmetic_id   = info.get("id", "")
        cosmetic_type = get_cosmetic_type(cosmetic_id)

        item_order_rank = item_order.index(cosmetic_type) if cosmetic_type in item_order else len(item_order)
        rarity_rank     = rarity_priority.get(rarity, 999)
        sub_rank        = sub_order.get(cosmetic_id, 9999)

        return (
            item_order_rank,
            rarity_rank,
            sub_rank
        )
    
    sorted_info_list = sorted(info_list, key=get_sort_key)
    return [info['id'] for info in sorted_info_list]

def filter_mythic_ids_func(items, converted_mythic_ids):
     
    mythic_items = []
    for item_type, ids_list in items.items():
        for cid in ids_list:

            if cid.lower() in mythic_ids or cid in converted_mythic_ids:
                mythic_items.append(cid)

    return mythic_items


async def get_cosmetic_info(cosmetic_id: str) -> dict:

        async with aiohttp.ClientSession(headers={"User-Agent": f"DeviceAuthGenerator/{platform.system()}/{platform.version()}"}) as session:

            async with session.request(
                method="GET",
                url=f"https://fortnite-api.com/v2/cosmetics/br/{cosmetic_id}"
            ) as response:
                 
                if response.status != 200:
                    return {
                        "id": cosmetic_id,
                        "rarity": "Unknown",
                        "name": "Unknown"
                    }
                
                data:dict = await response.json()

                rarity = data.get("data", {}).get("rarity", {}).get("displayValue", "Unknown")
                name   = data.get("data", {}).get("name", "Unknown")

                if cosmetic_id.lower() in mythic_ids:
                    rarity = "Mythic"

                if name == "Unknown":
                    name = cosmetic_id

                return {
                    "id"    : cosmetic_id,
                    "rarity": rarity,
                    "name"  : name
                }
        
Skins = skins()
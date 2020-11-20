from bs4 import BeautifulSoup
import pandas as pd
import json
from bs4 import BeautifulSoup
import requests
import pandas as pd
import aiohttp
import asyncio
import pyodbc
import psycopg2

with open("resources/settings.json", "r") as f:
    key = json.load(f)

conn_str = (
    "DRIVER={PostgreSQL ANSI(x64)};"
    "DATABASE=VinvestorData;"
    "UID=postgres;"
    f"PWD={key['Database']['passing']};"
    "SERVER=localhost;"
    "PORT=5432;"
)


async def get_site_content(currUrl):
    async with aiohttp.ClientSession() as session:
        async with session.get(currUrl) as resp:
            page = await resp.read()
    soup = BeautifulSoup(page, "lxml")
    return soup


def analyzeAndInsert(curr_url):

    loop = asyncio.get_event_loop()
    sites_soup = loop.run_until_complete(get_site_content(curr_url))
    # start process of getting info
    tds = sites_soup.find_all("td")
    general_info = tds[1].find_all("b")
    ChangWat = general_info[1].get_text()
    Saca = general_info[2].get_text()
    RopBanshee = general_info[3].get_text()
    chanode_num = tds[5].get_text()
    amphur = tds[7].get_text()
    naSamrut = tds[13].get_text()
    tambol = tds[15].get_text()
    rawang = f"{tds[20].get_text()} {tds[21].get_text()}"
    pan_ti = f"{tds[23].get_text()}"
    ma_tra_suan = f"{tds[25].get_text()}"
    din_num = f"{tds[27].get_text()}"
    zone = f"{tds[37].get_text()}"
    block = f"{tds[33].get_text()}"
    lot = f"{tds[35].get_text()}"
    area_rai_an_tarangwa = f"{tds[48].get_text()}"
    price_per_tarawa = f"{tds[57].get_text()}"
    price_per_tarawa = float(
        price_per_tarawa.replace("บาท", "").replace(",", ""),
    )
    # print(
    #     f"""
    #     ChangWat = {ChangWat}
    #     Saca = {Saca}
    #     RopBanshee = {RopBanshee}
    #     Chanode = {chanode_num}
    #     amphur = {amphur}
    #     naSamrut = {naSamrut}
    #     tambol = {tambol}
    #     rawant = {rawang}
    #     pan_ti = {pan_ti}
    #     ma_tra_suan = {ma_tra_suan}
    #     Ti Din = {din_num}
    #     zone = {zone}
    #     block = {block}
    #     lot = {lot}
    #     area = {area_rai_an_tarangwa}
    #     price = {price_per_tarawa}
    #     """
    # )
    # end process of gaining info

    loop.close()
    print(type(ChangWat))

    try:
        connection = psycopg2.connect(
            user=f"{key['Database']['USER']}",
            password=f"{key['Database']['passing']}",
            host="127.0.0.1",
            port="5432",
            database="VinvestorData",
        )
        cursor = connection.cursor()

        postgres_insert_query = """ 
        INSERT INTO public."Chanod_Data"(
        "InSiteURL", "จังหวัด", "สาขา", "รอบบัญชี", "โฉนดเลขที่", "อำเภอ", "หน้าสำรวจ", "ตำบล", "ระวาง", "แผ่นที่", "มาตราส่วน", "เลขที่ดิน", "โซน", "บล็อก", "ล็อท/หน่วย", "เนื้อที่(ไร่-งาน-ตร.วา)", "ราคาประเมิน (บาท ต่อ ตร.)")
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        record_to_insert = (
            curr_url,
            ChangWat,
            Saca,
            RopBanshee,
            chanode_num,
            amphur,
            naSamrut,
            tambol,
            rawang,
            pan_ti,
            ma_tra_suan,
            din_num,
            zone,
            block,
            lot,
            area_rai_an_tarangwa,
            price_per_tarawa,
        )
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        count = cursor.rowcount
        print(count, "Record inserted successfully into mobile table")

    except (Exception, psycopg2.Error) as error:
        if connection:
            print("Failed to insert record into mobile table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


# analyzeAndInsert(
#     "http://property.treasury.go.th/pvmwebsite/search_data/r_land_price.asp?landid=81020&changwat=81&amphur=04"
# )


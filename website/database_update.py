import pandas as pd
import socket
import requests
from urllib3.util import connection as urllib3_cn
import sqlite3
from pathlib import Path
import os


def allowed_gai_family():
    family = socket.AF_INET    # force IPv4
    return family


urllib3_cn.allowed_gai_family = allowed_gai_family


def remove_duplicated_flats(df):
    # removing duplicated flats
    duplicate = df.groupby(['address', 'storey_range', 'flat_type'])['month'].apply(
        list).reset_index(name='month_list')  # based on the groupby, make the duplicated months into a list
    month = list(duplicate['month_list'])
    new_month_list = []
    for i in range(len(month)):
        new_month_list.append(max(month[i]))
    print("length before remove dupe: ", len(df))
    print(len(new_month_list))
    new_df = pd.DataFrame(new_month_list, columns=['month'])
    print("DEBUG", new_df)
    #duplicate['month_list'] = max(duplicate['month_list'])
    duplicate['month_list'] = new_df
    duplicate = duplicate.rename(columns={'month_list': 'month'})

    duplicate = pd.merge(duplicate, df, on=[
        'address', 'storey_range', 'flat_type', 'month'])
    duplicate = duplicate.drop_duplicates(
        subset=['address', 'storey_range', 'flat_type', 'month'], keep='first')
    df = duplicate.reset_index(drop=True)
    df['price_per_sqm'] = df['resale_price']/df['floor_area_sqm']
    print(df.head())
    print("length aft remove dupe: ", len(df))
    return df


# uses onemap API to retrieve latitude, longitude and postal_code
def getcoordinates(address):
    req = requests.get('https://developers.onemap.sg/commonapi/search?searchVal=' +
                       address+'&returnGeom=Y&getAddrDetails=Y&pageNum=1')
    resultsdict = eval(req.text)
    if len(resultsdict['results']) > 0:
        return resultsdict['results'][0]['LATITUDE'], resultsdict['results'][0]['LONGITUDE'], resultsdict['results'][0]['POSTAL']
    else:
        pass


def appendcoordinates(df):
    coordinateslist = []
    count = 0
    failed_count = 0
    addresslist = list(df['address'])
    # append coordinates and address into DataFrame
    for address in addresslist:
        try:
            if len(getcoordinates(address)) > 0:
                count = count + 1
                print('Extracting', count, 'out of',
                      len(addresslist), 'addresses')
                coordinateslist.append(getcoordinates(address))
        except:
            count = count + 1
            failed_count = failed_count + 1
            print('Failed to extract', count, 'out of',
                  len(addresslist), 'addresses')
            coordinateslist.append(None)
    print('Total Number of Addresses With No Coordinates', failed_count)
    df_coordinates = pd.DataFrame(coordinateslist)
    # combined coordinates and postal code with original dataframe
    df_combined = pd.concat([df, df_coordinates], axis=1, join='outer')
    df_combined = df_combined .rename(
        columns={0: 'latitude', 1: 'longitude', 2: 'postal_code'})
    return df_combined


def appendcolumns(df_combined):
    df_combined['postal_sector'] = df_combined['postal_code'].str[:2]
    df_combined['numOfFavourites'] = 0
    df_combined['address_no_postal_code'] = df_combined['street_name'] + \
        " BLK " + df_combined['block']
    df_combined['address'] = df_combined['street_name'] + \
        " BLK " + df_combined['block'] + ' '+df_combined['postal_code']
    return df_combined


def update_values(update, old):
    compare_update = update[["address", "storey_range", "flat_type"]]
    compare_old = old[["address", "storey_range", "flat_type"]]

    compare_update_list = compare_update.values.tolist()
    compare_old_list = compare_old.values.tolist()

    print(compare_update_list[0])
    print(compare_old_list[0])

    duplicate_data = 0
    new_data = 0

    print(len(compare_update_list))
    for i in range(len(compare_update_list)):

        if compare_update_list[i] in compare_old_list:
            # get index of the old database
            index = compare_old.loc[(compare_old['address'] == compare_update_list[i][0]) & (compare_old['storey_range'] == compare_update_list[i][1]) & (
                compare_old['flat_type'] == compare_update_list[i][2])].index.values.astype(int)[0]
            # print(index)
            duplicate_data += 1
            # print("old price: ",old["resale_price"].iloc[index])
            # print("new:",update["resale_price"].iloc[i])
            # print("oldmonth:", old["month"].iloc[index])
            old.at[index, 'resale_price'] = update["resale_price"].iloc[i]
            old.at[index, 'price_per_sqm'] = update["price_per_sqm"].iloc[i]
            old.at[index, 'month'] = update["month"].iloc[i]
        #     print(old["resale_price"].iloc[index])
        #     print("newmonth:", old["month"].iloc[index])
        else:
            new_data += 1
            new_id = old['id'].values[-1] + 1
            # print("newid:",new_id)

            new_image = (old['image'].iloc[-1])
            new_image_number = (int(new_image[9]) + 1) % 6
            # print(new_image_number)
            new_row = update.iloc[[i]]
            new_row = new_row.copy()
            new_row['image'] = "hdb_image" + str(new_image_number) + ".jpg"
            new_row['id'] = new_id

            # print(new_row)
            old = pd.concat([old, new_row], axis=0)
    old = old.reset_index(drop=True)
    print(old)
    print(old.dtypes)
    print(f"duplicated data: {duplicate_data}")
    print(f"new data: {new_data}")
    return old


def database():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DROP TABLE flat")
    flat = pd.read_csv('merged.csv')
    flat.to_sql('flat', conn, if_exists='replace', index=False)


def main():
    cwd = Path(__file__).parent.absolute()
    print(cwd)
    os.chdir(cwd)
    df = pd.read_csv("flats.csv")
    # select a month to update
    month = input("Enter a month to update (YYYY-MM): ")
    df = df[(df['month'] >= month)]  # select the latest month
    df['address'] = df['street_name'] + " " + df['block']  # append address
    print("length intially: ", len(df))
    # df = df.head(20) #THIS IS FOR TESTING
    df = remove_duplicated_flats(df)  # remove the duplicated flats
    # find latitude, longitude and postal code
    df_combined = appendcoordinates(df)
    # append other columns such as numOfFavourites
    update = appendcolumns(df_combined)

    # update = update.head(20) #THIS IS FOR TESTING
    #update.to_csv('testrun.csv', index=False)
    print("update", update)
    old = pd.read_csv("merged.csv")  # load the old database
    # old = old.head(20) #THIS IS FOR TESTING
    database_csv = update_values(update, old)
    print("database_csv:", database_csv)
    database_csv.to_csv('merged.csv', index=False)
    database()


if __name__ == "__main__":
    main()

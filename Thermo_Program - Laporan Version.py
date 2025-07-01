from functions import *

import pandas as pd
import numpy as np
import pytesseract
import datetime

print('-----THERMOGRAPHY AUTOMATION PROGRAM-----\n')
while True:
    print('--MAIN MENU--')
    print('1: Check if tesseract is installed')
    print('2: Naming files')
    print('3: Reading temperature data')
    print('4: Equipment that not measured yet')
    print('5: Make empty folders')
    print('6: Exit\n')
    main = input('')
    print('\n')

    if main == '1':
        try:
            print('Tesseract is installed with version: ', end='')
            print(pytesseract.get_tesseract_version())
            print('\n')
        except pytesseract.TesseractNotFoundError:
            print("Please install tesseract first before you continue with the program\n")
        
    # ---------------------------------------------------------------------------------------------------------------------
    elif main == '2':
        # Naming Files based on Folders
        # Database Only for Naming Files
        path = os.path.join(os.getcwd(), 'System', 'Naming List.xlsx')
        # Read excel file
        name_df = pd.read_excel(path)
        name_df['Temperature'] = np.nan
        name_df.dropna(subset='Equipment', inplace=True)

        # Empty Dictionary
        equipment = dict()

        # Filling dictionary
        for x in range(name_df.shape[0]):
            eq = name_df.iloc[x]['Name']
            part = name_df.iloc[x]['Parts']
            if not equipment.get(eq):
                equipment[eq] = [part]
            else:
                equipment[eq].append(part)

        base = os.path.join(os.getcwd(), 'Photos', 'Main')
        if not os.path.exists(base):
            print('There ')
        print(f'used folder is {base} \n')

        # Remove Empty Folders
        remove_empty(base)

        folders = [f for f in os.listdir(base) if (os.path.isdir(os.path.join(base, f)) and f[0] != '.')]
        eqlist = set(equipment.keys())
        folders = set(folders)
        folders.intersection_update(eqlist)
        noeq = eqlist.difference(folders)

        count = 0
        changed = set()
        notnamed = []

        for f in folders:
            curfol = os.path.join(base, f)
            print('Naming files in folder: ' + f)
            
            if f in eqlist:
                name = f
            elif f.split()[0] in eqlist:
                name = f.split()[0]
            else:
                name = ''

            # Defining parts of equipment
            print('Equipment name: ' + name)
            parts = equipment[name]
            print(curfol)
            # Compare 
            datalength = len(os.listdir(curfol))
            partlen = len(parts)
            
            if datalength == partlen*2:
                print('iterate in folder \n' + f)
                for num,x in enumerate(os.listdir(curfol)):
                    try:
                        if num%2 == 0:
                            newname = f + ' - ' + equipment[name][num//2] + '.jpg'

                        elif num%2 == 1:
                            newname = f + ' - ' + equipment[name][num//2] + '(2).jpg'
                    except KeyError:
                        pass
                    if numbers_in_string(x) > 3:
                        changed.add(f)
                        path_oldname = os.path.join(curfol, x)
                        path_newname = os.path.join(curfol, newname)
                        os.rename(path_oldname, path_newname)
            else:
                print('Data and Part number is not matched: ', end='')
                print(str(datalength)+ ' vs '+str(partlen))

        # Extract Images and remove empty folders
        extract_image(base, changed)
        remove_empty(base)

        # List of equipment that is not changed
        notchanged = folders.difference(changed)

        folders = sorted(folders)
        noeq = sorted(noeq)
        changed = sorted(changed)
        notchanged = sorted(notchanged)

        while True:
            print('\nFile naming is done. See process results: ')
            print('1 : Equipment list')
            print('2 : Equipment with no data')
            print('3 : Equipment file name changed')
            print('4 : Equipment file name not changed because data is not matched')
            print('5 : Back to Main Menu')
            res = input('\n')

            if res == '1':
                print('Equipment data list: ')
                for f in folders:
                    print('\t- ' + f)
            elif res == '2':
                print('Equipment with no data: ')
                for f in noeq:
                    print('\t- ' + f)
            elif res == '3':
                print('Equipment that file name is changed: ')
                for f in changed:
                    print('\t- ' + f)
            elif res == '4':
                print('Equipment that name if NOT changed: ')
                if len(notchanged) == 0:
                    print('-')
                else:
                    for f in notchanged:
                        print('\t- ' + f)
            elif res == '5':
                break
            else:
                print('\nPlease choose between the number above\n')
        print('\n')

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    elif main == '3':
        # Reading Thermograph number

        # DataFrame for Temperature Values
        # This serves as base DataFrame for the sequence
        path = os.path.join(os.getcwd(), 'System', 'Data List.xlsx')
        df = pd.read_excel(path)
        df.set_index(['Equipment', 'Loc'], inplace=True)

        base = os.path.join(os.getcwd(), 'Photos', 'Main')
        photos = list(os.listdir(base))
        photos = [f for f in photos if '(2)' in f]

        path = os.path.join(base, photos[0])

        timestamp = os.path.getmtime(path)

        df.reset_index(inplace=True)

        df['Temperature v1'] = np.nan
        df['Temperature v2'] = np.nan

        files = [f for f in os.listdir(base) if ('.jpg' in f)]
        eq = ''

        for i in range(df.shape[0]):
            if eq != df.iloc[i]['Name']:
            
                eq = df.iloc[i]['Name']
                target_eq = [f for f in files if (eq in f)]
            else:
                pass
            
            part = df.iloc[i]['Parts']
            
            print('----------' + eq + ' - '+ part + '----------')
            
            if part == 'Tanggal':
                if len(target_eq) != 0:
                    dates = [t for t in target_eq if ('(2)' in t)]
                    path = os.path.join(base, dates[0])
                    timestamp = os.path.getmtime(path)
                    date = datetime.datetime.fromtimestamp(timestamp)
                    date = date.strftime('%d/%m/%Y')
                    
                    print('Tanggal: ' + date)
                    
                    df.loc[i,'Temperature v1'] = date
                    df.loc[i,'Temperature v2'] = date
                    
            else:
                target_part = [p for p in target_eq if (part in p and '(2)' not in p)]
                if len(target_part) == 1:
                    path = target_part[0]
                    path = os.path.join(base,path)
                    
                    temp = temp_reading(path, app=False)
                    df.loc[i, 'Temperature v1'] = temp
                    
                    temp = temp_reading(path, app=True)
                    df.loc[i, 'Temperature v2'] = temp
                    
                elif len(target_part) >= 2:
                    temps1 = []
                    temps2 = []
                    for x in target_part:
                        path = os.path.join(base, x)
                        temp1 = temp_reading(path, app=False)
                        temp2 = temp_reading(path, app=True)
                        
                        temps1.append(temp1)
                        temps2.append(temp2)
                    
                    temp1 = np.nanmax(temps1)
                    temp2 = np.nanmax(temps2)
                    
                    df.loc[i, 'Temperature v1'] = temp1
                    df.loc[i, 'Temperature v2'] = temp2
                        
                        
        #     print(eq + ' - ' + part)
        #     print(target_part)

        date_now = datetime.datetime.now()
        date = date_now.strftime('%d-%m-%Y')

        name = 'OUTPUT ' + date
        ext = '.xlsx'
        filename = name+ext
        print(filename+ext)
        file_path = os.path.join(os.getcwd(), filename)

        filenum = 1

        while os.path.exists(file_path):
            
            num = name + ' (' + str(filenum) + ')'
            filename = num + ext
            print(filename)
            file_path = os.path.join(os.getcwd(), filename)

            filenum += 1   
        df.to_excel(file_path)
        print('\n')

    # -----------------------------------------------------------------------------------------------------------------------------------------------------
    elif main == '4':
        # Check equipment that isnt measured yet
        # Database Only for Naming Files
        path = os.path.join(os.getcwd(), 'System', 'Naming List.xlsx')
        # Read excel file
        name_df = pd.read_excel(path)
        name_df['Temperature'] = np.nan
        name_df.dropna(subset='Equipment', inplace=True)
        # Equipment List for all, unit, and common
        eqlist = list(set(name_df['Name']))
                
        base = os.path.join(os.getcwd(), 'Photos', 'Main')
        jpg = [p for p in os.listdir(base) if p.endswith('.jpg')]

        item = [f.split('-')[0].strip() for f in jpg]
        item = set(item)
        eqlist = set(eqlist)

        not_taken = eqlist - item
        not_taken = list(not_taken)
        not_taken.sort()

        print('Equipment not measured yet: ')
        for n in not_taken:
            print('\t- ' + n)     
        print('\n')

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    elif main == '5':
        # Naming Files based on Folders
        # Database Only for Naming Files
        path = os.path.join(os.getcwd(), 'System', 'Naming List.xlsx')
        # Read excel file
        name_df = pd.read_excel(path)
        name_df['Temperature'] = np.nan
        name_df.dropna(subset='Equipment', inplace=True)

        # Function to make Empty Folder
        make_empty_folders(name_df)

    # ------------------------------------------------------------------------------------------------------------------------------------------------
    elif main == '6':
        print('Exitting...')
        break
    else:
        print('Please enter value from 1 to 5\n')
                    
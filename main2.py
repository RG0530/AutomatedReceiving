# See Code By Zapier documentation for implementation or editing.
# See README .txt file at following directory for implementation or editing:
    # sites/RFIDLabALECTeam105/Shared Documents/General/WMSupplierValidation/.Info
# Last updated on 7/20/2023 by Rayce Giles.
# Note that Python is not my strongsuit.


# Testing Fields
#input_data = {'alecvid' : 'ALECVID20230719010900023', 'files' : ',1\n\n,,,,\n2\n3,4,'}


# Input Fields
alecVID = input_data['alecvid']
files = input_data['files']


# Classes
# AlecEnumerator:
    # Built to handle enumerating over the ALECVID in search of departmentIDs, vendorIDs, hundreds, etc.
    # Also built to reliably handle exceptions.
class AlecEnumerator():


    # Fields
    _alecVID = ''
    vendors = vendorsExtra = vendorCut = departments = departmentsExtra = departmentCut = hundredsCut = ''
    hundreds = errorLog = ''
    idInfo = [['','',''],['','','']]


    # Methods
    # __init__:
        # Required for Python Classes. Kickstarts main() as well.
        # Also provides a final change in directory paths if an exception was ever caught.
        # _alecVID: ALECVID passed in to
    def __init__(__self__, _alecVID):
        __self__._alecVID = _alecVID
        __self__.main()
        if (__self__.errorLog):
            if (__self__.idInfo[0][0] == 'Critical Error'):
                __self__.idInfo = [['Critical Error', '-2', '-2'], ['Critical Error', '-2', '-2']];
            else:
                __self__.idInfo = [['Error', '-1', '-1'], ['Error', '-1', '-1']];
            __self__.hundreds = '00s'

    # config:
        # Defines the vendors, departments, etc. using variables for easy access around script.
        # Main variables to change when expanding. See .Info implementation documentation.
    def config(__self__):
        __self__.vendors = ('Submission Updates', 'Walmart US', 'Sams Club', 'Walmart Canada', 'Nordstrom', 'Dicks Sporting Goods')
        __self__.vendorsExtra = {'09' : 'General'}
        __self__.departments = {'Walmart US' : ('Empty', 'Apparel', 'Home', 'Electronics', 'Toys', 'Sporting Goods', 'Battery',
                                       'Tires', 'Entertainment', 'Hardline')}
        __self__.departmentsExtra = {'Walmart US' : {'46' : 'Example'}}

        __self__.vendorCut = [15,17]
        __self__.departmentCut = [17,19]
        __self__.hundredsCut = [19,-2]

        __self__.sharePointSite = "RFIDLab"
        __self__.sharePointDestination = "ALECTeam/General/Supplier Validation"


    # assignInfo:
        # Assigns the Vendor and Department information depending on the chars cut from the ALECVID.
        # Catches: Index Error (Cuts outside of ALECVID), Key Error (No vendor/dept.), and NameError (Code error)
    def assignInfo(__self__):
        try:
            __self__.idInfo[0] = __self__.assignIDs('vendors', None)
            if(len(__self__.idInfo[0])>3):
                __self__.idInfo[1] = ['Error','-1','-1']
                raise __self__.idInfo[0][3](__self__.idInfo[0][4])

            __self__.idInfo[1] = __self__.assignIDs('departments', __self__.idInfo[0][0])
            if(len(__self__.idInfo[1])>3):
                raise __self__.idInfo[1][3](__self__.idInfo[1][4])


        except IndexError as e: __self__.error(e, f"The {e.__str__()} cut is out of bounds!\n"
                                         f"The ALECVID is likely shorter than where the cut is "
                                         f"expected to be! Change the cuts in the config method!")
        except KeyError as e: __self__.error(e, e.__str__())
        except NameError as e: __self__.error(e, "Somehow, a string was passed into method 'assignIDs' for argument '_tableName'"
                                        "which turned into a variable that doesn't exist! \nThis string should ONLY either"
                                        "be 'vendors' or 'departments', and should not be touched!")


    # assignIDs:
        # Assigns information through assigning argument _tableName as variable from config files. Done for reusability.
        # In events of errors, returns variables early along with exceptions in an effort to preserve variables.
        # Raises: Index Error (Cuts outside of ALECVID), Key Error (No vendor/dept.), and NameError (Code error).
        # _tableName: Name of the table 'type' that will be used to grab info from (i.e. 'vendors' and 'departments').
        # _prevIDName: Name of the previous ID's name (aka Vendor Name) to access a dictionary's value (aka Departments).
    def assignIDs(__self__, _tableName, _prevIDName):
        rawID = '-1'; intID = '-1'; name = 'Error'

        # Note that incoming _tableName argument is converted into the config variables to make this method reusable.
        try:
            table = eval(f'__self__.{_tableName}')
            tableExtra = eval(f'__self__.{_tableName}Extra')
            cut = eval(f'__self__.{_tableName[:-1]}Cut')
        except NameError as e:
            return name, intID, rawID, NameError

        # Note that this will check if this method is being ran to search the 'departments' dictionary or other dicts.
        # If it is, it will jump into the correct value (which should be a tuple) depending on the vendorName (_prevIDName).
        # Upon jumping into the correct tuple, it continues and finds the correct department.
        # If there is no department list whose key matches the given vendorID (i.e. Sam's Club has no departments), it
        # skips the department search.
        if(type(table) is dict):
            if(_prevIDName in table):
                table = table[_prevIDName]
            else:
                return 'All Departments', 'A', 'A'

        #Everything following this comment is shared between 'vendors' and 'departments'

        if (len(__self__._alecVID) < cut[1]): return name, intID, rawID, IndexError, f"{_tableName}ID '{cut}'"
        rawID = __self__._alecVID[cut[0]:cut[1]]
        intID = int(rawID)

        if (intID > len(table)-1):
            if (rawID in tableExtra):
                name = tableExtra[rawID]
            else:
                additionalError = ''
                if(_prevIDName): additionalError = f" for vendor '{_prevIDName}'"
                return name, intID, rawID, KeyError, (f"The {_tableName[:-1]}ID "
                               f"'{intID.__str__()}'{additionalError} was not found in the '{_tableName}' "
                               f"tuple, and the raw {_tableName[:-1]}ID '{rawID}' "
                               f"was not found in the '{_tableName}Extra' dictionary! You will probably need to"
                               f"access the code and add/remove from the tuple or dictionary.")
        else:
            name = table[intID]
        return name, intID, rawID


    # grabHundreds:
        # Grabs the number of submissions by the hundreds. For instance, 21496 submissions = 21400 submissions, or 21400s.
        # Raises: Index Error (Cuts outside of ALECVID).
    def grabHundreds(__self__):
        if(len(__self__._alecVID)-1 < __self__.hundredsCut[0]):
            __self__.error(IndexError, f"The 'hundreds' cut '{__self__.hundredsCut}' is out of bounds!"
                                         f"The ALECVID is likely shorter than where the cut is "
                                         f"expected to be! Change the cuts in the config method!")
        __self__.hundreds = (__self__._alecVID[__self__.hundredsCut[0]:__self__.hundredsCut[1]] + '00s').strip("0")
        if (__self__.hundreds == 's'): __self__.hundreds = '00s'


    # error:
        # Creates the logs for an error if ever caught.
    def error(__self__, _exception, _message):
        __self__.errorLog = (f"BEGINNING OF ERROR LOG:\n{type(_exception)} \n{_message}\n\n"
                    f"<INPUT VARS>\nalecvid: {__self__._alecVID}\nfiles: Not Shown\n<CONFIG VARS>\nvendors: {__self__.vendors}\n"
                    f"vendorsExtra: {__self__.vendorsExtra}\nvendorCut: {__self__.vendorCut}\n"
                    f"departments: {__self__.departments}\ndepartmentsExtra: {__self__.departmentsExtra}"
                    f"\ndepartmentCut: {__self__.departmentCut}\nhundredsCut: {__self__.hundredsCut}\n"
                    f"<ID VARS>\nvendorIDRaw: {__self__.idInfo[0][2]}\nvendorID: {__self__.idInfo[0][1]}\n"
                    f"vendorName: {__self__.idInfo[0][0]}\ndepartmentIDRaw: "
                    f"{__self__.idInfo[1][2]}\ndepartmentID: {__self__.idInfo[1][1]}\n"
                    f"departmentName: {__self__.idInfo[1][0]}\nhundreds: {__self__.hundreds}\n\n"
                    f"Log system developed by Rayce Giles on 6/30/2023. See him if you have any questions.\n"
                    f"For more assistance, read the Code by Zapier documentation and the README .txt file at\n"
                    f"sites/RFIDLabALECTeam105/Shared Documents/General/Supplier Validation/Info")


    # main:
        # Drives the main code by calling each method in succession.
        # Also catches a final 'catch-all error' for the (hopefully) slim chance that an exception slips by except blocks.
    def main(__self__):
        try:
            __self__.config()
            __self__.assignInfo()
            __self__.grabHundreds()
        except Exception as e:
            __self__.idInfo = [['Critical Error','-2','-2'],['Critical Error','-2','-2']]; hundreds = '00s'
            __self__.error(e, "\nA critical error occured! An unknown exception slipped by and crashed"
                        f" the script!\nData should still be preserved.")


# FileStripper:
    # Designed to strip whitespace from lines of files and convert them into a list separated by newlines (\n).
class FileStripper():


    # Fields
    _files = ''


    # Methods
    # __init__:
        # Required for Python Classes. Kickstarts main() as well. Also appends the error log to be uploaded as well.
    def __init__(__self__, _files):
        __self__._files = _files
        __self__.main()


    def main(__self__):
        __self__._files = __self__._files.strip().strip(",").replace("\n",",")

        # Checks for repetitive commas
        filesStripped = ''
        for i, c in enumerate(__self__._files):
            if (((c == ',') and (len(__self__._files) >= i + 2) and not (__self__._files[i + 1] == ',')) or not (
                    c == ',')):
                filesStripped += c
        __self__._files = filesStripped


enum = AlecEnumerator(alecVID)
filesStripped = FileStripper(files)._files

return {"vendorName" : enum.idInfo[0][0], "departmentName" : f"{enum.idInfo[1][2]} - {enum.idInfo[1][0]}",
        "hundreds" : enum.hundreds, "files" : filesStripped, "errorLog" : enum.errorLog, "sharePointSite" :
         enum.sharePointSite, "sharePointDestination" : enum.sharePointDestination}

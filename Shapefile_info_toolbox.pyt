# -*- coding: utf-8 -*-
import arcpy
import os
import glob
from struct import *

#
# ツールから呼び出しするものをShapefileUtilクラスとして定義
#
class ShapefileUtil:
    @staticmethod
    def codepage_list_from_ldid(ldid):
        """
        LDID をもとに上記に整理したCodepage と Description を含めてリストとして返却
        """
        ldid_dic = {
            1:['437','US MS-DOS'],
            2:['850','International MS-DOS'],
            3:['1252','Windows ANSI Latin I'],
            4:['10000','Standard Macintosh'],
            8:['865','Danish OEM'],
            9:['437','Dutch OEM'],
            10:['850','Dutch OEM'],
            11:['437','Finnish OEM'],
            13:['437','French OEM'],
            14:['850','French OEM'],
            15:['437','German OEM'],
            16:['850','German OEM'],
            17:['437','Italian OEM'],
            18:['850','Italian OEM'],
            19:['932','Japanese Shift-JIS'],
            20:['850','Spanish OEM'],
            21:['437','Swedish OEM'],
            22:['850','Swedish OEM'],
            23:['865','Norwegian OEM'],
            24:['437','Spanish OEM'],
            25:['437','English OEM (Great Britain)'],
            26:['850','English OEM (Great Britain)'],
            27:['437','English OEM (US)'],
            28:['863','French OEM (Canada)'],
            29:['850','French OEM'],
            31:['852','Czech OEM'],
            34:['852','Hungarian OEM'],
            35:['852','Polish OEM'],
            36:['860','Portuguese OEM'],
            37:['850','Portuguese OEM'],
            38:['866','Russian OEM'],
            55:['850','English OEM (US)'],
            64:['852','Romanian OEM'],
            77:['936','Chinese GBK (PRC)'],
            78:['949','Korean (ANSI/OEM)'],
            79:['950','Chinese Big5 (Taiwan)'],
            80:['874','Thai (ANSI/OEM)'],
            87:['Current ANSI CP','ANSI'],
            88:['1252','Western European ANSI'],
            89:['1252','Spanish ANSI'],
            100:['852','Eastern European MS-DOS'],
            101:['866','Russian MS-DOS'],
            102:['865','Nordic MS-DOS'],
            103:['861','Icelandic MS-DOS'],
            104:['895','Kamenicky (Czech) MS-DOS'],
            105:['620','Mazovia (Polish) MS-DOS'],
            106:['737','Greek MS-DOS (437G)'],
            107:['857','Turkish MS-DOS'],
            108:['863','French-Canadian MS-DOS'],
            120:['950','Taiwan Big 5'],
            121:['949','Hangul (Wansung)'],
            122:['936','PRC GBK'],
            123:['932','Japanese Shift-JIS'],
            124:['874','Thai Windows/MS–DOS'],
            134:['737','Greek OEM'],
            135:['852','Slovenian OEM'],
            136:['857','Turkish OEM'],
            150:['10007','Russian Macintosh'],
            151:['10029','Eastern European Macintosh'],
            152:['10006','Greek Macintosh'],
            200:['1250','Eastern European Windows'],
            201:['1251','Russian Windows'],
            202:['1254','Turkish Windows'],
            203:['1253','Greek Windows'],
            204:['1257','Baltic Windows']
        }
        
        id_dict = ldid_dic.get(ldid)
        if id_dict == None:
            return [ldid, '0', 'Unknown CodePage']
        else:
            return [ldid, id_dict[0], id_dict[1]]

    @staticmethod
    def codepage_from_dbf_file(dbf):
        """
        dbf のヘッダーに記録されているLDID をもとにCodepage と Description を含めて返却
        """
        with open(dbf,'rb') as f:
            dat = f.read()
        ldid = unpack_from('<B', dat, 29)[0]
        return ShapefileUtil.codepage_list_from_ldid(ldid)

    @staticmethod
    def check_related_cpgfile(dbf):
        """
        cpg ファイルの存在チェックの関数
        （cpg ファイルが存在する場合はファイルの中身も一緒に取得して返す）
        """
        path, dbf_name = os.path.split(dbf) # path と ファイル名を分ける  
        file_name = os.path.splitext(dbf_name)[0]
        cpg_file_name = "{}.cpg".format(os.path.splitext(file_name)[0])
        cpg_file = os.path.join(path, cpg_file_name)
        bl_exist = os.path.isfile(cpg_file)
        code_value = ""
        if (bl_exist):
            with open(cpg_file, 'r') as f:
                code_value = f.readline().rstrip()
        return (bl_exist, code_value)

    @staticmethod
    def create_related_cpgfile(cpg_txt, dbf):
        """
        dbf ファイルと同じフォルダー内にcpg ファイルを作成
        """
        path, dbf_name = os.path.split(dbf) # path と ファイル名を分ける  
        file_name = os.path.splitext(dbf_name)[0]
        cpg_file_name = "{}.cpg".format(os.path.splitext(file_name)[0])
        cpg_file = os.path.join(path, cpg_file_name) #フルパス
        with open(cpg_file, 'w', encoding='utf-8') as f: # mode='w' でない場合には作成。既存のものがある場合は上書き
            f.write(cpg_txt)

    @staticmethod
    def delete_related_cpgfile(dbf):
        """
        dbf ファイルと同じフォルダー内にcpg ファイルを削除
        """
        path, dbf_name = os.path.split(dbf) # path と ファイル名を分ける  
        file_name = os.path.splitext(dbf_name)[0]
        cpg_file_name = "{}.cpg".format(os.path.splitext(file_name)[0])
        cpg_file = os.path.join(path, cpg_file_name) #フルパス
        if os.path.isfile(cpg_file): # 存在する場合に削除
            os.remove(cpg_file)


#
# ツールボックスの定義
#
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "シェープファイル（dBaseファイル） の文字化け原因調査と対策ツールボックス"
        self.alias = ""
        # List of tool classes associated with this toolbox
        self.tools = [LdidCpgInfoTool, BatchCpgTool, BatchCpgDelTool]

#
# 各ツールの定義
#
class LdidCpgInfoTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "シェープファイル（dBaseファイル）の LDID と CPGファイルの一覧表示ツール"
        self.description = "シェープファイル（dBaseファイル）の LDID（Language driver ID） と *.cpgファイルを一覧で表示するツールです"
        self.canRunInBackground = False
        
    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="フォルダー",
            name="folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="サブフォルダーを検索対象にする",
            name="subfolder",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param1.value = False #value で boolean 値として取得できるようデフォルト設定
        params = [param0, param1]
        return params
    
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
    
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return
    
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    
    def execute(self, parameters, messages):
        """The source code of the tool."""
        # パラメータを取得
        # arcpy.AddMessage([k.value for k in parameters])
        folder = parameters[0].valueAsText
        blSubfolder = parameters[1].value  # boolean 値として判定に使いたいので parameters[1].value で取得。 parameters[1].valueAsText でないよ

        # 処理
        files = []
        header = []
        if blSubfolder == False:
            dbf_files = glob.glob(folder + "/*.dbf") # フルパスのリスト
            header = ['ファイル名', 'LDID', 'Codepage', 'Description', 'CPGファイルの有無', 'CPGファイルの値']
            for dbf in dbf_files:
                arcpy.AddMessage(dbf)
                # LDIDと関連したCodepage の情報
                code = ShapefileUtil.codepage_from_dbf_file(dbf)
                path, dbf_name = os.path.split(dbf)
                code.insert(0, dbf_name) # list の先頭にファイル名を追加

                # CPG ファイルの情報
                cpg_exist, code_value = ShapefileUtil.check_related_cpgfile(dbf)
                code.append(cpg_exist)
                code.append(code_value)
                
                files.append(code)
        else:
            dbf_files = glob.glob(folder + "/**/*.dbf", recursive = True) # フルパスのリスト
            header = ['サブフォルダー名', 'ファイル名', 'LDID', 'Codepage', 'Description', 'CPGファイルの有無', 'CPGファイルの値']
            for dbf in dbf_files:
                # LDIDと関連したCodepage の情報
                code = ShapefileUtil.codepage_from_dbf_file(dbf)
                path, dbf_name = os.path.split(dbf)
                code.insert(0, os.path.split(path)[1]) # list の先頭にサブディレクトリを追加
                code.insert(1, dbf_name) # list の先頭にファイル名を追加

                # CPG ファイルの情報
                cpg_exist, code_value = ShapefileUtil.check_related_cpgfile(dbf)
                code.append(cpg_exist)
                code.append(code_value)
                
                files.append(code)

        #結果表示
        #別途インストールするのであれば tabulate, PrettyTable, texttable などを使うとよさそうだが。。。
        #https://tereshenkov.wordpress.com/2018/03/27/printing-pretty-tables-with-python-in-arcgis/
        arcpy.AddMessage("--------------------------------------------------------------------------------")
        if len(files) == 0:
            arcpy.AddWarning(u"指定フォルダーにはシェープファイル（dBaseファイル） がありません。")
        else:
            #リスト内包表記 - List comprehension でカンマ区切りで表示
            #https://chaingng.github.io/post/python_list_tab/
            msg = ",".join([str(_) for _ in header])
            arcpy.AddMessage(msg)
            for f in files:
                msg = ",".join([str(_) for _ in f])
                arcpy.AddMessage(msg)
        arcpy.AddMessage("--------------------------------------------------------------------------------")
        
        return

class BatchCpgTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "シェープファイル（dBaseファイル）用 cpgファイル の一括作成ツール"
        self.description = "シェープファイル（dBaseファイル）用 *.cpgファイルを一括で作成するツールです"
        self.canRunInBackground = False
        
    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="フォルダー",
            name="folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="サブフォルダーを検索対象にする",
            name="subfolder",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param1.value = False #valueAsText で boolean 値として取得できるようデフォルト設定
        param2 = arcpy.Parameter(
            displayName="cpgファイルの値（SJIS / UTF-8）",
            name="cpg_value",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        param2.filter.type = "ValueList" # ValueList で選択式にする
        param2.filter.list = ['SJIS', 'UTF-8'] # SJIS or UTF-8
        param2.value = 'SJIS'

        params = [param0, param1, param2]
        return params
    
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
    
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return
    
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    
    def execute(self, parameters, messages):
        """The source code of the tool."""
        # パラメータを取得
        folder = parameters[0].valueAsText
        blSubfolder = parameters[1].value  # boolean 値として判定に使いたいので parameters[1].value で取得。 parameters[1].valueAsText でないよ
        cpg_txt = '{}\n'.format(parameters[2].valueAsText)

        # 処理
        dbf_files = []
        if blSubfolder == False:
            dbf_files = glob.glob(folder + "/*.dbf") # フルパスのリスト
        else:
            dbf_files = glob.glob(folder + "/**/*.dbf", recursive = True) # フルパスのリスト

        # 結果の表示
        arcpy.AddMessage("--------------------------------------------------------------------------------")
        if len(dbf_files) == 0:
            arcpy.AddWarning(u"指定フォルダーにはcpgファイル の作成対象のシェープファイル（dBaseファイル） がありません。")
        else:
            for dbf in dbf_files:
                ShapefileUtil.create_related_cpgfile(cpg_txt, dbf)
            arcpy.AddMessage(u"{0} 件 の cpgファイル の作成を行いました。".format(len(dbf_files)))
        arcpy.AddMessage("--------------------------------------------------------------------------------")

        return

class BatchCpgDelTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "シェープファイル（dBaseファイル）用 cpgファイル の一括削除ツール"
        self.description = "シェープファイル（dBaseファイル）用 *.cpgファイルを一括で削除するツールです"
        self.canRunInBackground = False
        
    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="フォルダー",
            name="folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="サブフォルダーを検索対象にする",
            name="subfolder",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        param1.value = False #valueAsText で boolean 値として取得できるようデフォルト設定
        params = [param0, param1]
        return params
    
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True
    
    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return
    
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    
    def execute(self, parameters, messages):
        """The source code of the tool."""
        # パラメータを取得
        folder = parameters[0].valueAsText
        blSubfolder = parameters[1].value  # boolean 値として判定に使いたいので parameters[1].value で取得。 parameters[1].valueAsText でないよ

        # 処理
        dbf_files = []
        if blSubfolder == False:
            dbf_files = glob.glob(folder + "/*.dbf") # フルパスのリスト
        else:
            dbf_files = glob.glob(folder + "/**/*.dbf", recursive = True) # フルパスのリスト

        # 結果の表示
        arcpy.AddMessage("--------------------------------------------------------------------------------")
        if len(dbf_files) == 0:
            arcpy.AddWarning(u"指定フォルダーにはcpgファイル の削除対象のシェープファイル（dBaseファイル）がありません。")
        else:
            for dbf in dbf_files:
                ShapefileUtil.delete_related_cpgfile(dbf)
            arcpy.AddMessage(u"{0} 件 の cpgファイル の削除を行いました。".format(len(dbf_files)))
        arcpy.AddMessage("--------------------------------------------------------------------------------")

        return
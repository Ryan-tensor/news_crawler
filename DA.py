#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from concurrent import futures
import time
import argparse
import grpc
from google.protobuf import empty_pb2
import pymysql
import os

exe_path = os.path.realpath(sys.argv[0])
bin_path = os.path.dirname(exe_path)
lib_path = os.path.realpath(bin_path + '/../lib/python')
sys.path.append(lib_path)

from elsa.facade import userattr_pb2
from minds.maum.da import provider_pb2
from minds.maum.sds import sds_pb2

# import MySQLdb.cursors

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class Tutor_output_DA(provider_pb2.DialogAgentProviderServicer):                                                                    #### <---------- class 설정 DA 이름 설정
    # STATE
    # state = provider_pb2.DIAG_STATE_IDLE
    init_param = provider_pb2.InitParameter()

    # PROVIDER
    provider = provider_pb2.DialogAgentProviderParam()
    provider.name = 'academy_health'                                                                                                  #### <---------- provider이름 설정 해주는 것
    provider.description = 'ai_tutor'
    provider.version = '0.1'
    provider.single_turn = False
    provider.agent_kind = provider_pb2.AGENT_SDS
    provider.require_user_privacy = True

    # SDS Stub
    sds_server_addr = ''
    sds_stub = None
    print 'sds_stub'
    def __init__(self):
    	print 'init'
        self.state = provider_pb2.DIAG_STATE_IDLE
    #
    # INIT or TERM METHODS
    #

    def get_sds_server(self):
        print 'sds_server'
        sds_channel = grpc.insecure_channel(self.init_param.sds_remote_addr)
        # sds_channel = grpc.insecure_channel('127.0.0.1:9906')
        resolver_stub = sds_pb2.SpokenDialogServiceResolverStub(sds_channel)

        print 'stub'
        sq = sds_pb2.ServiceQuery()
        sq.path = self.sds_path
        sq.name = self.sds_domain
        print sq.path, sq.name

        svc_loc = resolver_stub.Find(sq)
        print 'find result', svc_loc
        # Create SpokenDialogService Stub
        print 'find result loc: ', svc_loc.server_address
        self.sds_stub = sds_pb2.SpokenDialogServiceStub(
            grpc.insecure_channel(svc_loc.server_address))
        self.sds_server_addr = svc_loc.server_address
        print 'stub sds ', svc_loc.server_address

    def IsReady(self, empty, context):
        print 'IsReady', 'called'
        status = provider_pb2.DialogAgentStatus()
        status.state = self.state
        return status

    def Init(self, init_param, context):
        print 'Init', 'called'
        self.state = provider_pb2.DIAG_STATE_INITIALIZING
        # COPY ALL
        self.init_param.CopyFrom(init_param)
        # DIRECT METHOD
        self.sds_path = init_param.params['sds_path']
        print 'path'
        self.sds_domain = init_param.params['sds_domain']
        print 'domain'

        self.db_host = init_param.params['db_host']
        print 'db_host'

        self.db_port = init_param.params["db_port"]
        print 'db_port'

        self.db_user = init_param.params['db_user']
        print 'db_user'

        self.db_pwd = init_param.params['db_pwd']
        print 'db_pwd'

        self.db_database = init_param.params['db_database']
        print 'db_database'

        self.db_table = init_param.params['db_table']
        print 'db_table'
        # CONNECT
        self.get_sds_server()
        print 'sds called'
        self.state = provider_pb2.DIAG_STATE_RUNNING
        # returns provider
        result = provider_pb2.DialogAgentProviderParam()
        result.CopyFrom(self.provider)
        print 'result called'
        return result

    def Terminate(self, empty, context):
        print 'Terminate', 'called'
        # DO NOTHING
        self.state = provider_pb2.DIAG_STATE_TERMINATED
        return empty_pb2.Empty()

    #
    # PROPERTY METHODS
    #

    def GetProviderParameter(self, empty, context):
        print 'GetProviderParameter', 'called'
        result = provider_pb2.DialogAgentProviderParam()
        result.CopyFrom(self.provider)
        return result

    def GetRuntimeParameters(self, empty, context):
        print 'GetRuntimeParameters', 'called'
        params = []
        result = provider_pb2.RuntimeParameterList()

        sds_path = provider_pb2.RuntimeParameter()
        sds_path.name = 'sds_path'
        sds_path.type = userattr_pb2.DATA_TYPE_STRING
        sds_path.desc = 'DM Path'
        sds_path.default_value = 'academy_health'                                                                                      #### <---------- sds 경로 설정 (SDS 파일 이름 넣어주기)
        sds_path.required = True
        params.append(sds_path)

        sds_domain = provider_pb2.RuntimeParameter()
        sds_domain.name = 'sds_domain'
        sds_domain.type = userattr_pb2.DATA_TYPE_STRING
        sds_domain.desc = 'DM Domain'
        sds_domain.default_value = 'academy_health'                                                                                   #### <---------- Domain 이름 설정해주기(SDS와 동일하게 넣어줄것)
        sds_domain.required = True
        params.append(sds_domain)

        db_host = provider_pb2.RuntimeParameter()  # 사용할 DB서버 설정
        db_host.name = 'db_host'
        db_host.type = userattr_pb2.DATA_TYPE_STRING
        db_host.desc = 'Database Host'
        db_host.default_value = 'ai-tutor.cxofzcpmqwoz.us-west-2.rds.amazonaws.com'
        db_host.required = True
        params.append(db_host)

        db_port = provider_pb2.RuntimeParameter()
        db_port.name = 'db_port'
        db_port.type = userattr_pb2.DATA_TYPE_STRING
        db_port.desc = 'Database Port'
        db_port.default_value = '3306'
        db_port.required = True
        params.append(db_port)

        db_user = provider_pb2.RuntimeParameter()
        db_user.name = 'db_user'
        db_user.type = userattr_pb2.DATA_TYPE_STRING
        db_user.desc = 'Database User'
        db_user.default_value = 'aitutor'
        db_user.required = True
        params.append(db_user)

        db_pwd = provider_pb2.RuntimeParameter()
        db_pwd.name = 'db_pwd'
        db_pwd.type = userattr_pb2.DATA_TYPE_STRING
        db_pwd.desc = 'Database Password'
        db_pwd.default_value = 'aitutor12'
        db_pwd.required = True
        params.append(db_pwd)

        db_database = provider_pb2.RuntimeParameter()  #DB 스키마 이름
        db_database.name = 'db_database'
        db_database.type = userattr_pb2.DATA_TYPE_STRING
        db_database.desc = 'Database Database name'
        db_database.default_value = 'tutor'
        db_database.required = True
        params.append(db_database)

        db_table = provider_pb2.RuntimeParameter()    #DB 해당 테이블 이름                                                  ##########qqqqqqqq
        db_table.name = 'db_table'
        db_table.type = userattr_pb2.DATA_TYPE_STRING
        db_table.desc = 'Database table'
        db_table.default_value = 'academy_intro'                                                                                     #### <---------- DB에서 사용할 테이블 이름을 넣어줄 것
        db_table.required = True
        params.append(db_table)

        result.params.extend(params)
        return result

    def Talk(self, talk, context):
        meta_data = {"out.embed.type": "", "out.embed.data.body": ""}   # meta data 초기화 => 여기서 meta data란 text형식으로 보여주는 것 이외에 비디오, 이미지, 음악재생 등의 추가 정보를 제공해 줄 수 있는 데이터
        flag = False                                                    # 예외처리 변수(flag == True 예외처리 발생)

        self.get_sds_server()                                           # sds 와의 연동
        print '------- [talk 시작] --------'
        print 'talk ==> ', talk

        session_id = talk.session_id
        print "Session ID : " + str(session_id)  # 해당 session id
        print "[Question] ", talk.text  # talk.text -> 질문 내용
        print "Access_from", str(talk.access_from)  # 접속 경로( 안드로이드, ios, 스피커, 웹, console 등에 따라 다른 값으로 저장)

        # Create DialogSessionKey & set session_key
        dsk = sds_pb2.DialogueSessionKey()
        dsk.session_key = session_id
        print '<create session key for dialog>'

        # Dialog Open
        sds_session = self.sds_stub.Open(dsk)          # sds에서 설정해준 시나리오 open
        print '<Open the dialog>'

        sq = sds_pb2.SdsQuery()
        sq.session_key = sds_session.session_key
        sq.utter = talk.text

        # Dialog UnderStand
        sds_act = self.sds_stub.Understand(sq)  # => 대화에 대한 전반적인 log. ex) 사용하는 slot

        # DB Connection
        conn = pymysql.connect(user=self.db_user,
                               password=self.db_pwd,
                               host=self.db_host,
                               database=self.db_database,
                               charset='utf8',
                               use_unicode=False)

        curs = conn.cursor()     # '현재 위치'를 포함하는 데이터 요소

        # 변수 설정
        bmi = ''                                                                                               #### <---------- 사용할 변수 설정해 줄 것.
        weight = None
        height = None
        dialog_act = ''
        output = ''


        # Create SdsSlots & set Session Key
        sds_slots = sds_pb2.SdsSlots()
        sds_slots.session_key = sds_session.session_key
        print sds_act.filled_slots
        print '< sds_act > ', sds_act
        # Copy filled_slot to result Slot & Fill information slots

        for k, v in sds_act.filled_slots.items():  # sds_act.filled_slots == user에 의해서 채워진 slot
            sds_slots.slots[k] = v
        print '< sds_slots.slots > ', sds_slots.slots
        #########################################수정할 부분
        weight = sds_act.filled_slots.get('user.wt')
        print sds_act.filled_slots.get('user.wt')
        print '< user.wt slot >', weight
        height = sds_act.filled_slots.get('user.ht')
        print sds_act.filled_slots.get('user.ht')
        print '< user.ht slot >', height

        # Dialog Act
        best_slu = sds_act.origin_best_slu                          # slu 값 중에서 가장 높은 값을 표현(Best SLU)
        print '< best_slu > ' + best_slu
        dialog_act = best_slu[best_slu.find('#') + 1:best_slu.find('(')]    # DA TYPE을 이용하기 위한 파싱
        print '< dialog_act > ' + dialog_act

        if dialog_act == 'affirm' and weight is not None and height is not None:                                                                                            #### <---------- 대화 의도에 따른 조건 설정
            sds_slots.slots['output'] = output
            sdsUtter = self.sds_stub.FillSlots(sds_slots)
            sdsUtter.response = output
        ###############여기까지 채울부분
        else:
            sdsUtter = self.sds_stub.FillSlots(sds_slots)                       # 위의 동작으로 인해 변해진 (혹은 채워진) sds_slot 들을 sds_utter값에 할당 함
            print '< sds_utter >', sdsUtter

        print "[System output] " + sdsUtter.response    # sdsUtter == sds에서 정의해 놓은 대답들을 제공해 준다. 단 sdsUtter에서 슬롯들이 채워져서 변했다면, 변한 부분이 적용되어 제공해 준다.

        talk_res = provider_pb2.TalkResponse()
        talk_res.text = sdsUtter.response
        print '< talK_res >', talk_res  # TALK response 상에서 출력되는 값


        print '----------------------- [TALK 끝] -------------------'

        if str(talk_res.text[-6:-1]) == '[END]':           # 최종 출력문에서 [END]가 있을 경우
            talk_res.state = provider_pb2.DIAG_CLOSED                   # 대화 상태 종료로 인한 close
            self.sds_stub.Close(dsk)                                    # 위와 동일
            talk_res.text = talk_res.text[:-6]                          # 최종 발화문전달
            print '< talk_res.talk >', talk_res.text

        curs.close()
        conn.close()

        talk_res.meta['out.embed.type'] = meta_data['out.embed.type']  # 추가적인 meta_data 타입 정의
        talk_res.meta['out.embed.data.body'] = meta_data['out.embed.data.body']
        return talk_res

    def Close(self, req, context):
        print 'Closing for ', req.session_id, req.agent_key
        talk_stat = provider_pb2.TalkStat()
        talk_stat.session_key = req.session_id
        talk_stat.agent_key = req.agent_key

        ses = sds_pb2.DialogueSessionKey()
        ses.session_key = req.session_id
        self.sds_stub.Close(ses)
        return talk_stat

def serve():
    print 'start serve'
    parser = argparse.ArgumentParser(description='Tutor_output DA')
    print 'parser'
    parser.add_argument('-p', '--port',
                        nargs='?',
                        dest='port',
                        required=True,
                        type=int,
                        help='port to access server')
    print 'parser.add_argument'
    args = parser.parse_args()
    print 'args'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    print 'server'
    provider_pb2.add_DialogAgentProviderServicer_to_server(Tutor_output_DA(),
                                                           server)
    print 'add_dialogagebtorivuder'

    listen = '[::]' + ':' + str(args.port)
    print 'listen'
    server.add_insecure_port(listen)
    print 'add_insecure_port'
    server.start()
    print 'start'
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\x12\x04\x63hat\"!\n\rClientRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"!\n\x0e\x43lientResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x1e\n\x0b\x43hatRequest\x12\x0f\n\x07\x63hat_id\x18\x01 \x01(\t\"\x1f\n\x0c\x43hatResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x07\n\x05\x45mpty\"!\n\x10\x43hatListResponse\x12\r\n\x05\x63hats\x18\x01 \x03(\t2\x84\x02\n\x0b\x43hatService\x12=\n\x0eRegisterClient\x12\x13.chat.ClientRequest\x1a\x14.chat.ClientResponse\"\x00\x12?\n\x10GetClientAddress\x12\x13.chat.ClientRequest\x1a\x14.chat.ClientResponse\"\x00\x12=\n\x12SubscribeGroupChat\x12\x11.chat.ChatRequest\x1a\x12.chat.ChatResponse\"\x00\x12\x36\n\rDiscoverChats\x12\x0b.chat.Empty\x1a\x16.chat.ChatListResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_CLIENTREQUEST']._serialized_start=20
  _globals['_CLIENTREQUEST']._serialized_end=53
  _globals['_CLIENTRESPONSE']._serialized_start=55
  _globals['_CLIENTRESPONSE']._serialized_end=88
  _globals['_CHATREQUEST']._serialized_start=90
  _globals['_CHATREQUEST']._serialized_end=120
  _globals['_CHATRESPONSE']._serialized_start=122
  _globals['_CHATRESPONSE']._serialized_end=153
  _globals['_EMPTY']._serialized_start=155
  _globals['_EMPTY']._serialized_end=162
  _globals['_CHATLISTRESPONSE']._serialized_start=164
  _globals['_CHATLISTRESPONSE']._serialized_end=197
  _globals['_CHATSERVICE']._serialized_start=200
  _globals['_CHATSERVICE']._serialized_end=460
# @@protoc_insertion_point(module_scope)
#!/bin/bash
#protoc --proto_path=./ --java_out=../java/src/ descriptor.proto
#protoc --proto_path=./ --java_out=../java/src/ gaia_object.proto
#protoc --proto_path=./ --java_out=../java/src/ router.proto
#protoc --proto_path=./ --java_out=../java/src/ module.proto
#protoc --proto_path=./ --java_out=../java/src/ data.proto
#protoc --proto_path=./ --java_out=../java/src/ PiX.proto
#protoc --proto_path=./ --java_out=../java/src/ oceanus.proto
#protoc --proto_path=./ --java_out=../java/src/ native.proto
#protoc --proto_path=./ --java_out=../java/src/ flow.proto
#protoc --proto_path=./ --java_out=../java/src/ advert.proto
#
#protoc --proto_path=./ --python_out=../python/ descriptor.proto
#protoc --proto_path=./ --python_out=../python/ gaia_object.proto
#protoc --proto_path=./ --python_out=../python/ router.proto
#protoc --proto_path=./ --python_out=../python/ module.proto
#protoc --proto_path=./ --python_out=../python/ data.proto
#protoc --proto_path=./ --python_out=../python/ PiX.proto
#protoc --proto_path=./ --python_out=../python/ native.proto
#protoc --proto_path=./ --python_out=../python/ flow.proto
#protoc --proto_path=./ --python_out=../python/ oceanus.proto
#protoc --proto_path=./ --python_out=../python/ advert.proto
#protoc --proto_path=./ --python_out=../python/ callerid.proto

#for daVinci
#WORKSPACE=../../../
#protoc --proto_path=./ --python_out=${WORKSPACE}/daVinci/adx/src/py/resources module.proto
#protoc --proto_path=./ --python_out=${WORKSPACE}/daVinci/adx/src/py/resources data.proto
#protoc --proto_path=./ --python_out=${WORKSPACE}/daVinci/adx/src/py/resources gaia_object.proto
#protoc --proto_path=./ --python_out=${WORKSPACE}/daVinci/adx/src/py/resources descriptor.proto

#for gaia
#protoc --proto_path=./ --python_out=../../gaia/src/baseclient/python/ PiX.proto

#for matrix and daVinci news html
protoc --proto_path=./ --python_out=../ html_data.proto

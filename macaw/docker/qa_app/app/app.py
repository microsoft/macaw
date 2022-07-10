#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import logging
import sys
from typing import Optional

from flask import Flask, request, Response
from flask_restful import reqparse, Api, Resource

import remote_module

app = Flask("remote module")
api = Api(app)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)


class RemoteModule(Resource):

    def get(self):
        return 200

    def post(self):
        t0 = time.time()

        args = request.get_json(force=True)
        print(f"post request arguments {args}")
        validation = self.__validate_input(args)
        if validation:
            return validation, 500

        ret = {}
        ret.update(self.__get_response(args))
        ret["performance"] = time.time() - t0
        ret["error"] = False
        return ret, 200

    @staticmethod
    def __validate_input(args: dict) -> Optional[dict]:
        message = ""
        for ctx in remote_module.get_required_context():
            if not args.get(ctx):
                message = "Context missing: " + ctx
        if message:
            return {
                "message": message,
                "error": True
            }
        return None

    @staticmethod
    def __get_response(msg) -> dict:
        response = remote_module.handle_message(msg)
        app.logger.info("remote model result: %s", response)
        return response


api.add_resource(RemoteModule, '/')

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=os.environ.get('REMOTE_MODULE_PORT') or 8003)

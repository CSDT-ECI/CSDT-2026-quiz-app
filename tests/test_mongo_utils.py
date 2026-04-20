"""Tests for app/modules/mongo.py Mongo_Utils.init_app."""
import pytest
from flask import Flask


def test_init_app_raises_when_mongodb_uri_missing():
    """init_app without MONGODB_URI should raise RuntimeError (line 13)."""
    from app.modules.mongo import Mongo_Utils

    app = Flask(__name__)
    app.config.pop("MONGODB_URI", None)
    util = Mongo_Utils()
    with pytest.raises(RuntimeError, match="MONGODB_URI not found"):
        util.init_app(app)


def test_init_app_raises_when_mongodb_uri_empty():
    """Empty MONGODB_URI is treated as missing."""
    from app.modules.mongo import Mongo_Utils

    app = Flask(__name__)
    app.config["MONGODB_URI"] = ""
    util = Mongo_Utils()
    with pytest.raises(RuntimeError, match="MONGODB_URI not found"):
        util.init_app(app)

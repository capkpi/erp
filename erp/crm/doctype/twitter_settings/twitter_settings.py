# Copyright (c) 2020, CapKPI Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import json

import capkpi
import tweepy
from capkpi import _
from capkpi.model.document import Document
from capkpi.utils import get_url_to_form
from capkpi.utils.file_manager import get_file_path
from tweepy.error import TweepError


class TwitterSettings(Document):
	@capkpi.whitelist()
	def get_authorize_url(self):
		callback_url = (
			"{0}/api/method/erp.crm.doctype.twitter_settings.twitter_settings.callback?".format(
				capkpi.utils.get_url()
			)
		)
		auth = tweepy.OAuthHandler(
			self.consumer_key, self.get_password(fieldname="consumer_secret"), callback_url
		)
		try:
			redirect_url = auth.get_authorization_url()
			return redirect_url
		except tweepy.TweepError as e:
			capkpi.msgprint(_("Error! Failed to get request token."))
			capkpi.throw(
				_("Invalid {0} or {1}").format(capkpi.bold("Consumer Key"), capkpi.bold("Consumer Secret Key"))
			)

	def get_access_token(self, oauth_token, oauth_verifier):
		auth = tweepy.OAuthHandler(self.consumer_key, self.get_password(fieldname="consumer_secret"))
		auth.request_token = {"oauth_token": oauth_token, "oauth_token_secret": oauth_verifier}

		try:
			auth.get_access_token(oauth_verifier)
			self.access_token = auth.access_token
			self.access_token_secret = auth.access_token_secret
			api = self.get_api()
			user = api.me()
			profile_pic = (user._json["profile_image_url"]).replace("_normal", "")

			capkpi.db.set_value(
				self.doctype,
				self.name,
				{
					"access_token": auth.access_token,
					"access_token_secret": auth.access_token_secret,
					"account_name": user._json["screen_name"],
					"profile_pic": profile_pic,
					"session_status": "Active",
				},
			)

			capkpi.local.response["type"] = "redirect"
			capkpi.local.response["location"] = get_url_to_form("Twitter Settings", "Twitter Settings")
		except TweepError as e:
			capkpi.msgprint(_("Error! Failed to get access token."))
			capkpi.throw(_("Invalid Consumer Key or Consumer Secret Key"))

	def get_api(self):
		# authentication of consumer key and secret
		auth = tweepy.OAuthHandler(self.consumer_key, self.get_password(fieldname="consumer_secret"))
		# authentication of access token and secret
		auth.set_access_token(self.access_token, self.access_token_secret)

		return tweepy.API(auth)

	def post(self, text, media=None):
		if not media:
			return self.send_tweet(text)

		if media:
			media_id = self.upload_image(media)
			return self.send_tweet(text, media_id)

	def upload_image(self, media):
		media = get_file_path(media)
		api = self.get_api()
		media = api.media_upload(media)

		return media.media_id

	def send_tweet(self, text, media_id=None):
		api = self.get_api()
		try:
			if media_id:
				response = api.update_status(status=text, media_ids=[media_id])
			else:
				response = api.update_status(status=text)

			return response

		except TweepError as e:
			self.api_error(e)

	def delete_tweet(self, tweet_id):
		api = self.get_api()
		try:
			api.destroy_status(tweet_id)
		except TweepError as e:
			self.api_error(e)

	def get_tweet(self, tweet_id):
		api = self.get_api()
		try:
			response = api.get_status(tweet_id, trim_user=True, include_entities=True)
		except TweepError as e:
			self.api_error(e)

		return response._json

	def api_error(self, e):
		content = json.loads(e.response.content)
		content = content["errors"][0]
		if e.response.status_code == 401:
			self.db_set("session_status", "Expired")
			capkpi.db.commit()
		capkpi.throw(
			content["message"],
			title=_("Twitter Error {0} : {1}").format(e.response.status_code, e.response.reason),
		)


@capkpi.whitelist(allow_guest=True)
def callback(oauth_token=None, oauth_verifier=None):
	if oauth_token and oauth_verifier:
		twitter_settings = capkpi.get_single("Twitter Settings")
		twitter_settings.get_access_token(oauth_token, oauth_verifier)
		capkpi.db.commit()
	else:
		capkpi.local.response["type"] = "redirect"
		capkpi.local.response["location"] = get_url_to_form("Twitter Settings", "Twitter Settings")

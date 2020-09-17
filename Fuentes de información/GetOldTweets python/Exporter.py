# -*- coding: utf-8 -*-
import sys,getopt,datetime,codecs
if sys.version_info[0] < 3:
    import got
else:
    import got3 as got
    import json
    import os

def main(argv):

	if len(argv) == 0:
		print('You must pass some parameters. Use \"-h\" to help.')
		return

	if len(argv) == 1 and argv[0] == '-h':
		f = open('exporter_help_text.txt', 'r')
		print(f.read())
		f.close()

		return

	try:
		opts, args = getopt.getopt(argv, "", ("username=", "near=", "within=", "since=", "until=", "querysearch=", "toptweets", "maxtweets=","lang=", "output="))

		tweetCriteria = got.manager.TweetCriteria()
		outputFileName = "output_got.json"

		for opt,arg in opts:
			if opt == '--username':
				tweetCriteria.username = arg

			elif opt == '--since':
				tweetCriteria.since = arg

			elif opt == '--until':
				tweetCriteria.until = arg

			elif opt == '--querysearch':
				tweetCriteria.querySearch = arg

			elif opt == '--toptweets':
				tweetCriteria.topTweets = True

			elif opt == '--maxtweets':
				tweetCriteria.maxTweets = int(arg)
			
			elif opt == '--near':
				tweetCriteria.near = '"' + arg + '"'
			
			elif opt == '--within':
				tweetCriteria.within = '"' + arg + '"'

			elif opt == '--within':
				tweetCriteria.within = '"' + arg + '"'
			
			elif opt == '--lang':
				tweetCriteria.lang = arg

			elif opt == '--output':
				outputFileName = arg
				
		outputFile = codecs.open(outputFileName, "w+", "utf-8")

		# outputFile.write('username;date;retweets;favorites;text;geo;mentions;hashtags;id;permalink')
		print('Searching...\n')
		outputFile.write('[')
		
		def receiveBuffer(tweets,contador):
			for t in tweets:
				tweet={
					"_id": t.id, 
					"created_at": t.formatted_date,
					"id_str": t.id, 
					"text": t.text
				}
				tweet_j = json.dumps(tweet)
				outputFile.write('%s,'%(tweet_j))
				#agregar corchetes y quitar coma del final
				#outputFile.write(('\n{ "_id": "%s", "created_at": "%s","id": "%s","id_str": "%s", "text" : "%s" },' % (t.id, t.formatted_date, t.id, t.id, t.text)))#, t.geo, t.mentions, t.hashtags, t.id, t.permalink)))
			outputFile.flush()
			#contador += len(tweets)
			print('More %d saved on file...\n' % len(tweets))
			print('Total tweets %d saved on file...\n' % contador)
		contador = 0
		got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer,contador)

	except arg:
		print('Arguments parser error, try -h' + arg)
	finally:
		outputFile.seek(-1, os.SEEK_END)
		outputFile.truncate()
		outputFile.write(']')
		outputFile.close()
		print('Done. Output file generated "%s".' % outputFileName)

if __name__ == '__main__':
	main(sys.argv[1:])

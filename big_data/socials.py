import requests, scrapetube, time, httpx, asyncio
from flask import Flask


start_time = time.time()

class imageView():
    def __init__(self, images):
        self.images: list = images

    def display_images(self):
        app = Flask(__name__)

        @app.route('/')
        def index():
            img_tags = ''.join([f'<img alt="err rendering img" src="{img}" style="max-width: 250px; max0height: 250px; margin: 20px;">' for img in self.images])
            return f'<html><body>{img_tags}</body></html>'

        app.run(port=5500)
        return

class llsum:
    def __init__(self, text, llama_url="https://llm-chat-app-template.dfmata2010.workers.dev/api/chat"):
        self.llama_url: str = llama_url
        self.text: list = text

    async def summarize(self):
        summaries = []
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:  # Use an asynchronous HTTP client
            tasks = []
            for i in self.text:
                payload = {
                    "messages": [{
                        "role": "user",
                        "content": f"summarize this please:\n{i}"
                    }]
                }
                # Create a task for each HTTP request
                tasks.append(client.post(self.llama_url, json=payload))
            
            # Run all tasks concurrently
            responses = await asyncio.gather(*tasks)

            # Process responses
            for resp in responses:
                if resp.status_code == 200:
                    summaries.append(resp.json().get('response', ''))
                    print("success")
                else:
                    summaries.append("")
                    print(f"Request failed with status code {resp.status_code}")
        
        self.summaries = summaries
        return summaries
    
    def final_summary(self):
        print("Starting final summary...")
        print(self.summaries)
        combined_summary = ' '.join(self.summaries)
        payload = {
            "messages": [{
                "role": "user",
                "content": f"summarize this please:\n{combined_summary}"
            }]}
        
        resp = requests.post(self.llama_url, json=payload)
        print(resp.status_code)
        if resp.status_code in [403, "403"]:
            print('failed')
            return False
        else:
            final_sum = resp.json()['response']
            print("final success")
        
        return final_sum


class yt_parse:
    def __init__(self, channel_name):
        self.channel_name = channel_name

    def channel_scrape(self):
        #list comp attempt
        # self.vid_ids = [i['videoId'] for i in scrapetube.get_channel(channel_name=f"https://www.youtube.com/@{self.channel_name}/videos")]
        url = f"https://www.youtube.com/@{self.channel_name}/videos"
        resp = scrapetube.get_channel(channel_url=url)
        
        self.vid_ids = []
        for i in resp:
            self.vid_ids.append(i['videoId'])
        return self.vid_ids

    def get_transcript(self): #one liner: possible kinda
        self.transcripts = retl = []

        for v_id in self.vid_ids:
            ses = requests.Session() #btw this speeds it up A LOT bc it reuses TCP connection instead oopening a new one every time
            payload = {
                "videoUrl": f"https://www.youtube.com/watch?v={v_id}",
                "langCode": "en"
            }
            main_url = "https://tactiq-apps-prod.tactiq.io/transcript" #external caption ai api
            try:
                resp = ses.post(main_url, json=payload)
                retl.append(' '.join([i["text"] for i in resp.json()["captions"]]))
                print(f"Fetched transcript for {v_id}")
            except Exception as e:
                print(f"Failed to fetch transcript for {v_id}: {e}")
        return retl

class ig_scrape: # https://www.scrapingdog.com/blog/scrape-instagram/
    def __init__(self, username):
        self.link = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    def get_imgs(self):
        url = self.link
        insta_arr=[]
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "x-ig-app-id": "936619743392459",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            allData = response.json()['data']['user']
            allPosts=allData['edge_owner_to_timeline_media']['edges']

            for i in range(0,len(allPosts)):
                if(allPosts[i]['node']['is_video']!=True):
                    insta_arr.append(allPosts[i]['node']['display_url'])
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        return insta_arr


CR = ig_scrape('clashroyale')
v = imageView(CR.get_imgs())
v.display_images()
exit()

vid = yt_parse("CodeBullet")
channel = vid.channel_scrape()
transcripts = vid.get_transcript()

summarizer = llsum(transcripts)
asyncio.run(summarizer.summarize())
final_summary = summarizer.final_summary()
print(final_summary)



print(f"--- {time.time() - start_time} seconds ---")

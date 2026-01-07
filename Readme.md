# Immospider
Immospider is a python program that crawls the Immoscout24 website. You can also use it to
immediately receive an email when new apartments are available at the Immoscout24 website.
It is based on ideas from <http://mfcabrera.com/data_science/2015/01/17/ichbineinberliner.html>
and <https://github.com/balzer82/immoscraper> .

## Installation

Immospider is using the popular python framework <https://scrapy.org/> . For installation you need Python 3. Then you can
clone this repository and install the requirements via

pipenv install

This should install all necessary packages for you.

## Simple scraping
Let's assume you want to move to Berlin. You are searching for a flat with 2-3 rooms bigger than 60m^2 flat which should not be
more expensive than 1000 Euro. You must enter these requirements in Immoscout24 website and search. If you search for
whole Berlin you probably will find more than 500 results. As next step copy the url of your Immoscout search, because
Immospider will use it. For the example given here the url is
<https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Berlin/Berlin/-/2,50-/60,00-/EURO--1000,00> .
With this information you can now start Immospider like

scrapy crawl immoscout -o apartments.csv -a url=https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Berlin/Berlin/-/2,50-/60,00-/EURO--1000,00  -L INFO

You should be able to scrape all results within 30 seconds. The results will be stored as CSV file
`apartments.csv`.

## Scraping at regular intervals with email alarm

### Prerequisites

- Docker
- Account at SendGrid (for sending out email)

### Configuration
Make a copy of `config.tmpl` and rename it to `config`. Edit `config` and
file out the following environment variables:

URL=<your immoscout search url>
FROM=<from email address>
TO=<to email address>
SENDGRID_API_KEY=<your sendgrid API key>

By default Immospider is configured to run every 10 minutes. To change it edit the
file `yacrontab.yaml` and edit the line

schedule: "*/10 * * * *"

### Usage
To create the docker container and run it with your configuration do

$ sh run_docker.sh

This will create a docker container from the `Dockerfile`, install the dependencies
and Immospider into the container and run it with your configuration. It will scrape
the Immoscout24 in regular intervals, store the results and will send out an email
when it detects new results it hasn't seen before. Neat, isn't it?

### Running at Amazon EC2
To deploy the docker container in an Amazon EC2 instance you can do the following:

Create an instance with

Amazon Linux
Image Size 8GB
t2.micro

Configure it to allow for SSH access from your machine

security group (ssh-from-my-ip) SSH TCP 22 <your IP>/32

Start your instance and login to it with your private key `<your_keyfile>.pem

$ chmod 400 <your_keyfile>.pem
$ ssh -i "<your_keyfile>.pem" ec2-user@ec2-<your_instance_name>.<your_compute_zone>.compute.amazonaws.com

Then install Docker onto your VM instance

$ sudo yum update -y
$ sudo yum install -y docker
$ sudo service docker start

Finally clone this repository, create and run the docker container

$ git clone https://github.com/asmaier/ImmoSpider.git
$ cd ImmoSpider
# don't forget to change your configuration first
$ sudo sh run_docker.sh

See also

- <https://www.ybrikman.com/writing/2015/11/11/running-docker-aws-ground-up/#launching-an-ec2-instance>
- <https://docker-curriculum.com/#docker-on-aws>
- <https://techsparx.com/software-development/docker/deploy-images-without-registry.html>


## Computing travel times
Finding a good flat which is near to your work place and is also near to e.g. the kindergarden/school of your kids, your
favorite park etc. can be very difficult. Unfortunately the existing search engines in Germany for apartments like
Immoscout, Immowelt, Immonet don't support computing the travel time for an apartment to several destinations. Here I
want to show you how to use Immospider to do that.

You need an API key for the googlemaps API, if you want to compute travel times to several destinations.
You should follow the instructions at <https://github.com/googlemaps/google-maps-services-python#api-keys> to get
your API key.

Let's assume you want to move to Berlin. You will work at some fancy startup near Alexanderplatz but your partner likes
to go shopping at the KaDeWe. And you are searching for a flat with 2-3 rooms bigger than 60m^2 flat which should not be
more expensive than 1000 Euro. You must enter these requirements in Immoscout24 website and search. If you search for
whole Berlin you probably will find more than 500 results. As next step copy the url of your Immoscout search, because
Immospider will use it. For the example given here the url is
<https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Berlin/Berlin/-/2,50-/60,00-/EURO--1000,00> .
With this information you can now start Immospider like

scrapy crawl immoscout -o apartments.csv -s GM_KEY=<Google Maps API Key> -a url=https://www.immobilienscout24.de/Suche/S-T/Wohnung-Miete/Berlin/Berlin/-/2,50-/60,00-/EURO--1000,00 -a dest="Alexanderplatz, Berlin" -a mode=transit -a dest2="KaDeWe, Berlin" -L INFO

The option `-o apartments.csv` specifies the output file. The parameter `-s GM_KEY=<Google Maps API Key>` sets your
Google maps API key. The argument `dest="Alexanderplatz, Berlin" -a mode=transit` tells Immospider that you want to
calculate the travel time for each apartment to Alexanderplatz using public transportation mode. The
argument `dest2="KaDeWe, Berlin"` will additionaly compute the travel time via car (the default mode) to KaDeWe. You
can have up to three destinations `dest1,dest2,dest3` and specify the mode for each destination `mode1,mode2,mode3`.
The argument `-a url=...` must hold the search url from Immoscout. The optional parameter `-L INFO` can be added to
generate more log output.

If you start Immospider with the given parameters here it might run up to 20 minutes, not because the crawler is slow,
but because the Google Maps API takes some time to compute the travel time for each of the more than 500 apartments.
If that is too slow for you, you should modify your search on Immoscout (and again copy the new url), so that the
amount of search results is lower. If your result set is about 50 apartments, Immospider will only need 1-2 minutes
to compute all the travel times.


## Data Science
How one can analyze the search results you can see in several jupyter
notebooks
- [ImmoAnalyze.ipynb](https://nbviewer.jupyter.org/github/asmaier/ImmoSpider/blob/master/immoscience/ImmoAnalyze.ipynb) .
- [ImmoPredict.ipynb](https://nbviewer.jupyter.org/github/asmaier/ImmoSpider/blob/master/immoscience/ImmoPredict.ipynb) .
- [ApartmentsPredict.ipynb](https://nbviewer.jupyter.org/github/asmaier/ImmoSpider/blob/master/immoscience/ApartmentsPredict.ipynb) .
- [ImmoPredictHouses.ipynb](https://nbviewer.jupyter.org/github/asmaier/ImmoSpider/blob/master/immoscience/ImmoPredictHouses.ipynb) .


## Enhanced Features

### Telegram Integration
Immospider now supports Telegram notifications for both successful runs and failures. To use this feature:

1. Set the following environment variables:
   - `TELEGRAM_API_TOKEN`: Your Telegram bot API token
   - `TELEGRAM_CHAT_ID`: The chat ID where messages should be sent
   - `API_KEY`: Your API key for authentication
   - `API_URL`: The URL of the API (default: http://127.0.0.1:8000)

2. The system will send messages containing:
   - Basic apartment information (title, price, size)
   - Link to the apartment
   - LLM analysis of the apartment description
   - Personalized message for contacting the owner

3. Failure notifications are sent automatically when the spider run fails.

### LLM Analysis Pipeline
The system integrates with the Helmholtz LLM endpoint to analyze apartment descriptions. For each apartment, it generates:

- Strengths and biggest problems
- Location assessment
- Price-to-benefits rating
- Key points extracted from descriptions for personal messages
- Personalized messages using templates

The LLM analysis uses the BLABLADOR_API_KEY environment variable to authenticate with the Helmholtz LLM endpoint.

### Gradio Web Interface
A Gradio web interface has been added for easy configuration and control:

1. Access the interface at http://localhost:7860 (or your server's IP address)
2. The interface has three tabs:
   - Configuration: Set search parameters (URL, destination, mode, contact name)
   - Control: Manually trigger the spider
   - About: Information about the system
3. Changes are saved via the API endpoint

### Enhanced Safety Net
The system includes enhanced monitoring to ensure reliability:

1. The scraper runs every 15 minutes via yacron scheduler
2. If the scraper fails to run, a failure message is sent via Telegram
3. The cycle is reset when manually triggered
4. Both success and failure notifications are sent via Telegram

## Deployment

### Docker Deployment
The application is containerized using Docker. The Dockerfile has been updated to:

1. Install Gradio
2. Expose ports 8000 (API) and 7860 (Gradio interface)
3. Run both yacron (for scheduling) and the Gradio app simultaneously

To build and run the container:

```bash
docker build -t immospider .
docker run -d -p 8000:8000 -p 7860:7860 \
  -e API_KEY=your_api_key \
  -e TELEGRAM_API_TOKEN=your_telegram_token \
  -e TELEGRAM_CHAT_ID=your_chat_id \
  -e BLABLADOR_API_KEY=your_llm_api_key \
  immospider
```

### Environment Variables
The following environment variables are used:

- `API_KEY`: API key for authentication
- `API_URL`: URL of the API
- `TELEGRAM_API_TOKEN`: Telegram bot API token
- `TELEGRAM_CHAT_ID`: Telegram chat ID for notifications
- `BLABLADOR_API_KEY`: API key for Helmholtz LLM endpoint
- `GM_KEY`: Google Maps API key (optional, for travel time calculations)

## Testing
A test script is available to verify all functionality. Run it with:

```bash
python test_immospider.py
```

The test script verifies:
- API endpoints are working
- Configuration can be updated
- Spider can be triggered
- Telegram notifications are configured
- LLM analysis is functioning

## License

MIT License

Copyright (c) 2024 Asmaier

Permission is hereby granted, free of charge, to any person obtaining a copy
d of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

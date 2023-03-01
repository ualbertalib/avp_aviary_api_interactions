# AVP Aviary API Interactions

The repository contains quickly written scripts designed to interact with the [AVP Aviary](https://www.aviaryplatform.com/api/v1/documentation) audio/video repository software. These scripts, as of March 2023 are only proof-of-concept.

## Requirments

* Python 3
* ability to work with proof-of-concept level software

## Upload a media file via the API

The following script authenticates against the Aviary API and via chunking, uploads a media file. This approach only works for media files below 1G (maybe up to 2G at times) due to security and configuration restrictions on the Aviary side (according to Feb. 2023 conversations with AVP)

``` bash
python3 aviary_media_api_upload_chunked.py --server ${aviary_server_name}
```

## List metadata about a media item (could be extended to generate reports)

The following script authenticates against the Aviary API and prints out the media metadata of a specified media object

``` bash
python3 aviary_media_api_get.py --server ${aviary_server_name} --media_id ${media_id}
```

## To generate test media objects

The ffmpeg tool can be used to generate test video in cases where one requires a video of a certain size without copyright or permission encumbrances.

For example, the following creates a video of a testsrc with a 10sec duration at a 30 frames/second rate. By varying the duration, one can increase the storage size of the resulting video.

```
ffmpeg -f lavfi -i testsrc=duration=10:size=1280x720:rate=30 testsrc_10.mpg
```

Another option is to concatenate multiple videos together using ffmpeg and the concat feature that takes as input a file listing the vidoes to concatenate (one-per-line) and the output file.

``` bash
ffmpeg -f concat -safe 0 -i ffmpeg_concat.txt -c copy 3g.mp4
```

# AVP Aviary API Interactions

The repository contains quickly written scripts designed to interact with the [AVP Aviary](https://www.aviaryplatform.com/api/v1/documentation) audio/video repository software. These scripts, as of March 2023 are only proof-of-concept.

## Requirements

* Python 3
* ability to work with proof-of-concept level software

## Upload a media file via the API

The following script authenticates against the Aviary API and via chunking, uploads a media file. This approach only works for media files below 1G (maybe up to 2G at times) due to security and configuration restrictions on the Aviary side (according to Feb. 2023 conversations with AVP)

* Sometime after Aug/Sept tests and before Feb 2023, the API upload seems to have broken
  * the filename was made a required parameter (not in the release notes)
  * the API upload occurs without error but the media does not appear in the web UI and the resource media listing the Web UI throws an error page after the API upload

``` bash
python3 aviary_media_api_upload_chunked.py --server ${aviary_server_name} --input input.sample.csv
```

## List metadata about a media item (could be extended to generate reports)

The following script authenticates against the Aviary API and prints out the media metadata of a specified media object

``` bash
python3 aviary_media_api_get.py --server ${aviary_server_name} --media_id ${media_id}
```

## Get the `updated_at` field for resources (`updated_at` is unavailable via the web UI as of 2023-03-27)

For input, use the Web UI resource table option to export. This obtains a list of resource IDs.

``` bash
python3 aviary_api_report_resources_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

An attempt to use the Aviary API `/api/v1/collections` and `/api/v1/collections/{:collection_id}/resources` to build a list of resources failed (2023-03-27) due to a limit of 100 resources returned and no documentation on how to enable pagination.

``` bash
python3 aviary_api_report_resources_csv.py --server ${aviary_server_name} --output ${output_path}
```

For a JSON-like output (more for debugging)

``` bash
python3 aviary_api_report_resources_json.py --server ${aviary_server_name} --output ${output_path}
```

## Get the `updated_at` field for media and other metadata

For input, use the Web UI resource table option to export. This obtains a list of resource IDs.

``` bash
python3 aviary_api_report_media_csv_by_list.py --server ${aviary_server_name} --output ${output_path} -input ${input_path}
```

An attempt to use the Aviary API `/api/v1/collections` and `/api/v1/collections/{:collection_id}/resources` to build a list of media failed (2023-03-27) due to a limit of 100 resources returned and no documentation on how to enable pagination (similar to the resource report).

``` bash
python3 aviary_api_report_media_csv.py --server ${aviary_server_name} --output ${output_path}
```




## To generate test media objects

The ffmpeg tool can be used to generate test videos in cases where one requires a video of a certain size without copyright or permission encumbrances.

For example, the following creates a video of a testsrc with a 10sec duration at a 30 frames/second rate. By varying the duration, one can increase the storage size of the resulting video.

```
ffmpeg -f lavfi -i testsrc=duration=10:size=1280x720:rate=30 testsrc_10.mpg
```

Another option is to concatenate multiple videos together using ffmpeg and the `concat` feature that takes as input a file listing the vidoe files to concatenate (one-per-line) and the output file.

``` bash
ffmpeg -f concat -safe 0 -i ffmpeg_concat.txt -c copy 3g.mp4
```

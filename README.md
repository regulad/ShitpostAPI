# ShitpostAPI

An API for making quick edits of media, normally memes, to create a new type of media commonly referred to as a shitpost.

## Hosting

Docker is the preferred way to host an instance of the API.

Environment Variables:

* `SHITPOST_API_PORT`: Configures the webserver port. Default is `8081`.
* `SHITPOST_API_HOST`: Configures the webserver host. Default is `0.0.0.0`.
* `SHITPOST_API_URI`: MongoDB connection URI. Default is `mongodb://localhost:27107`.
* `SHITPOST_API_DB`: MongoDB database name. Default is `shitposts`.
* `SHITPOST_API_CACHE`: Relative (or absolute) path of the file cache. Default is `downloads/`

## API

### POST `/edit`

Returns a stream of bytes from a multipart request to edit a video.

Form fields:

* Media:
    * Type: Bytes
    * Content: The media you wish to edit, in bytes. Limited to 20MB, for performance reasons.
    * Headers:
        * Content-Type: The MIME type of the media. Currently, `video/mp4` is supported.
* Edits:
    * Type: String
    * Content: A JSON-Encoded string of the commands you wish to execute and their values.
    * Headers:
        * Content-Type: application/json
    
Edits example:

```json
{
  "edits": [
    {
      "name": "caption",
      "parameters": {
        "top": "Some string, eh?"
      }
    }  
  ]
}
```

If an edit's parameters are incorrect, it will continue to the next edit. If you don't want to pass any arguments, simply pass an empty object.

```json
{}
```

### GET `/commands`

Returns JSON data detailing available commands.

Example return:

```json
{
  "commands": [
    {
      "name": "caption",
      "parameters": [
        {
          "name": "top",
          "type": null
        },
        {
          "name": "bottom",
          "type": null
        }
      ],
      "description": "Appends text in impact font the top or bottom of an image."
    }
  ]
}
```

A `null` parameters means that the command does not take arguments.

A `null` type means that either the type cannot be translated into a string, or it takes any type.

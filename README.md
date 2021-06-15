# ShitpostAPI

An API for making quick edits of media, normally memes, to create a new type of media commonly referred to as a shitpost.

## Hosting

Docker is the preferred way to host an instance of the API.

Environment Variables:

* `SHITPOST_API_PORT`: Configures the webserver port. Default is `8081`.
* `SHITPOST_API_HOST`: Configures the webserver host. Default is `0.0.0.0`.
* `SHITPOST_API_URI`: MongoDB connection URI. Default is `mongodb://mongo`.
* `SHITPOST_API_DB`: MongoDB database name. Default is `shitposts`.
* `SHITPOST_API_CACHE`: Relative (or absolute) path of the file cache. Default is `downloads/`

## API

### Limiting

To protect against abuse and optimize performance, the API enforces some rate-limits.

**Every hour**:

* You may make 90 requests.
* Each request may be 20 megabytes in size or smaller.

If you exceed your 90 requests per hour, you will be unable to make any more requests until time expires.

Three headers are sent back in each response:

* `X-RateLimit-Limit`: The maximum amount of requests you can make in one period. By defualt, this is 90.
* `X-RateLimit-Remaining`: The remaining requests in the current period.
* `X-RateLimit-Reset`: Time until the end of the period, in seconds.

### Privacy

IP addresses are stored in the `users` collection of the database.

No other sensitive information is stored with this IP address, besides information critical to operation like basic metrics and rate limit data.

### Endpoints

#### GET `/`

Return the lines of this file: `README.md`.

#### GET `/user`

Returns all the data on you that is stored in the database. Yay, transparency!

#### POST `/edit`

Returns a stream of bytes from a multipart request to edit a video.

Form fields:

* Media:
    * Type: Bytes
    * Content: The media you wish to edit, in bytes. Limited to 20MB, for performance reasons.
    * Headers:
        * Content-Type: The MIME type of the media.
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

#### GET `/commands`

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


### GET `/commands/{command_name}`

Same as `commands`, but it looks up a single command.

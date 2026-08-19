// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Tiny Tapeout LTD
// Author: Kristaps Jurkans

export default eventHandler(async (event) => {
    const {shuttle} = event.context.params;
    const {format} = getQuery(event);
    const url = `https://app.tinytapeout.com/api/shuttles/${shuttle}/map?format=${format ? format : 1}`;

    const response = await fetch(url);
    if (!response.ok) {
        throw createError({status: 404, message: 'Not Found'});
    }

    const svg = await response.text();
    return new Response(svg, {
        headers: {
            'content-type': 'image/svg+xml',
            'cache-control': 'public, max-age=86400'    // cache image for 1 day (= 86400 seconds)
        }
    });
})
// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Tiny Tapeout LTD
// Author: Uri Shaked

import indexJson from '../../../index/index.json';

export default eventHandler((event) => {
  return indexJson;
});

// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Tiny Tapeout LTD
// Author: Uri Shaked

import { getShuttles } from '../model/shuttle';

export default eventHandler(() => {
  return getShuttles();
});

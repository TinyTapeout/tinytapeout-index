// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Tiny Tapeout B.V.
// Author: Uri Shaked

import analogPinoutsJson from '../../../index/analog_pinouts.json';
import { getShuttleInfo } from './shuttle';

interface IBoardAnalogPinout {
  description: string;
  /** Label of each analog pin on the board, by internal analog index (as listed in a project's `analog_pins`) */
  pin_labels: string[];
}

export interface IAnalogPinout extends IBoardAnalogPinout {
  /** Board the shuttle's chips ship on, a key of index/analog_pinouts.json */
  board: string;
}

const analogPinouts: Record<string, IBoardAnalogPinout> = analogPinoutsJson;

export function getAnalogPinout(shuttleId: string): IAnalogPinout | null {
  const board = getShuttleInfo(shuttleId)?.board;
  return board ? { board, ...analogPinouts[board] } : null;
}

/** Board label of each of the project's analog pins, parallel to `analog_pins` */
export function getAnalogPinLabels(shuttleId: string, analogPins: number[]) {
  const pinout = getAnalogPinout(shuttleId);
  return pinout ? analogPins.map((index) => pinout.pin_labels[index]) : [];
}

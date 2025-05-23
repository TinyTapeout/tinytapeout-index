import indexJson from '../../../index/index.json';
import unknownShuttle from '../model/unknown.json';

/** In legacy shuttles, the info.yaml files were committed after the fact, to a different path */
export const legacyShuttles = ['tt02', 'tt03', 'tt03p5'];

/** In older shuttles, the docs were embedded in info.yaml */
export const oldDocsShuttles = [...legacyShuttles, 'tt04', 'tt05'];

export interface IShuttleIndex {
  version: 3;
  id: string;
  name: string;
  repo: string;
  commit: string;
  updated: string;
  projects: IShuttleIndexProject[];
}

export interface IShuttleIndexProject {
  /** The type of the project, the default is 'project' */
  type?: 'project' | 'group' | 'subtile';
  macro: string;
  address: number;
  title: string;
  author: string;
  description: string;
  clock_hz: number;
  tiles: string;
  analog_pins: string[];
  repo: string;
  commit: string;
  pinout: Record<string, string>;
  danger_level?: 'safe' | 'medium' | 'high' | 'unknown';
  danger_reason?: string;
  subtile_group?: string;
  subtile_addr?: number;
  subtile_addr_bits?: number;
}

export function getShuttles() {
  return indexJson;
}

export function getShuttleInfo(id: string) {
  return indexJson.shuttles.find((shuttle) => shuttle.id === id);
}

export async function loadShuttleIndex(id: string) {
  if (id === 'unknown') {
    return unknownShuttle as IShuttleIndex;
  }
  const response = await fetch(
    `https://raw.githubusercontent.com/TinyTapeout/tinytapeout-index/main/index/${id}.json`,
  );
  if (!response.ok) {
    return null;
  }
  return (await response.json()) as IShuttleIndex;
}

export function getProjectBaseUrl(shuttle: string, project: string) {
  const shuttleRepo = getShuttleInfo(shuttle)?.repo;
  if (!shuttleRepo) {
    return null;
  }

  const rawUrl = shuttleRepo.replace('github.com', 'raw.githubusercontent.com');
  const branch = shuttle === 'tt02' ? shuttle : 'main';
  const projectsDir = legacyShuttles.includes(shuttle) ? 'project_info' : 'projects';
  return `${rawUrl}/${branch}/${projectsDir}/${project}`;
}

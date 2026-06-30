export interface Writing {
  title: string;
  date: string;
  collection: string;
  tags: string[];
  url: string;
  original: string;
  body: string;
}

export interface SearchResult {
  writing: Writing;
  score: number;
}

export type WorkspaceMode = 1 | 2 | 3 | 4 | 5 | 6;

export interface CountryItem {
  id: number;
  country_code: string;
  Country_Name: string;
  images?: string;
  trending?: boolean;
}

export interface PhoneNumberItem {
  id: number | string;
  ToNumber: string;
  country_name: string;
  release_time?: string;
}

export interface SMSMessageItem {
  ToNumber: string;
  FromNumber: string;
  Messagebody: string;
  message_time: string;
}

export interface TrafficCall {
  id: number;
  time: string;
  endpoint: string;
  code: string;
  desc: string;
  data: Record<string, any>;
}

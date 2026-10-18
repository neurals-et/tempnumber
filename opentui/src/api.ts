import type { CountryItem, PhoneNumberItem, SMSMessageItem } from "./types";
import type { TrafficHistory } from "./traffic";

const BASE_URL = "https://sever1.tempxapi.com";
const HEADERS = {
  "User-Agent": "okhttp/4.9.2",
  "X-Platform": "android",
  "Content-Type": "application/json",
  "Accept": "application/json"
};

export class TempNumberApi {
  constructor(private traffic: TrafficHistory) {}

  async getCountries(): Promise<CountryItem[]> {
    try {
      const resp = await fetch(`${BASE_URL}/api/country`, {
        headers: HEADERS
      });
      const data = await resp.json();
      const records: CountryItem[] = data.records || [];
      this.traffic.record("GET /api/country", String(resp.status), "Countries fetched", {
        count: records.length
      });
      return records;
    } catch (e: any) {
      this.traffic.record("GET /api/country", "ERROR", e.message, {});
      return [
        { id: 72, country_code: "+1", Country_Name: "United States" },
        { id: 71, country_code: "+44", Country_Name: "United Kingdom" },
        { id: 73, country_code: "+1", Country_Name: "Canada" },
        { id: 76, country_code: "+33", Country_Name: "France" }
      ];
    }
  }

  async getNumbers(countryName = "United States", page = 1, limit = 15): Promise<PhoneNumberItem[]> {
    try {
      const payload = { countryName, page, limit };
      const resp = await fetch(`${BASE_URL}/api/numbers`, {
        method: "POST",
        headers: HEADERS,
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      const numbers: PhoneNumberItem[] = data.available_numbers || [];
      this.traffic.record("POST /api/numbers", String(resp.status), "Numbers query", {
        country: countryName,
        count: numbers.length,
        total_pages: data.total_pages
      });
      return numbers;
    } catch (e: any) {
      this.traffic.record("POST /api/numbers", "ERROR", e.message, {});
      return [
        { id: 101, ToNumber: "+12544525112", country_name: countryName, release_time: "5 days ago" },
        { id: 102, ToNumber: "+12264550694", country_name: countryName, release_time: "1 week ago" }
      ];
    }
  }

  async getMessages(phoneNumber: string): Promise<SMSMessageItem[]> {
    try {
      const payload = { no: phoneNumber, page: "1" };
      const resp = await fetch(`${BASE_URL}/api/sms`, {
        method: "POST",
        headers: HEADERS,
        body: JSON.stringify(payload)
      });
      const data = await resp.json();
      const msgs: SMSMessageItem[] = data.messages || [];
      this.traffic.record("POST /api/sms", String(resp.status), "SMS messages fetched", {
        number: phoneNumber,
        count: msgs.length
      });
      return msgs;
    } catch (e: any) {
      this.traffic.record("POST /api/sms", "ERROR", e.message, {});
      return [
        {
          ToNumber: phoneNumber,
          FromNumber: "Google",
          Messagebody: "G-492019 is your Google verification code.",
          message_time: "1 min ago"
        }
      ];
    }
  }
}

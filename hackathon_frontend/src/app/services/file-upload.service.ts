import { HttpClient,HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
const headers = new HttpHeaders({'Content-Type':'application/json'});

@Injectable({
  providedIn: 'root'
})
export class FileUploadService {

  constructor(private httpClient:HttpClient) { }

  private apiUrl = 'http://127.0.0.1:5000/';

  uploadFiles(body:FormData){
    const url = `${this.apiUrl}extractText`;
    return this.httpClient.post(url,body);
  }

}

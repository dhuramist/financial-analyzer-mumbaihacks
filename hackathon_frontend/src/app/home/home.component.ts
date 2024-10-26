import { Component, ElementRef,ViewChild,ChangeDetectorRef  } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HistoryComponent } from '../history/history.component';
import { FileUploadService } from '../services/file-upload.service';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { NgxSpinnerService } from 'ngx-spinner';
import { CommonModule } from '@angular/common';
import Typed from 'typed.js';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [HistoryComponent, CommonModule, ReactiveFormsModule,NgxSkeletonLoaderModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {

  @ViewChild('typingElement') typingElement!: ElementRef;

  UploadFileForm = new FormGroup({
    companyName: new FormControl('', Validators.required),
    file: new FormControl(null, Validators.required)
  });

  summary: string | null = null;
  fileError: string | null = null;
  UploadFormsubmitted: boolean = false;
  showSummary: boolean = false;
 showSkeleton:boolean = true;
  analysis:string=``;
  companyName:string | null | undefined= null;
  get h() { return this.UploadFileForm.controls; }

  constructor(private fileuploadService: FileUploadService, private cdr: ChangeDetectorRef,private sanitizer: DomSanitizer, private spinner: NgxSpinnerService ) { }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      if (file.type === 'application/pdf') {
        this.UploadFileForm.patchValue({ file });
        this.UploadFileForm.get('file')?.setErrors(null);
        this.fileError = null;
      } else {
        this.UploadFileForm.get('file')?.setErrors({ fileType: true });
        this.fileError = 'Only PDF files are allowed';
      }
    }
  }
  
  onFilesSubmit() {
    if (this.UploadFileForm.invalid) {
      this.UploadFormsubmitted = true;
      return;
    }
    this.UploadFormsubmitted = false;

    const formData = new FormData();
    
    const fileControl = this.UploadFileForm.get('file');
    if (fileControl?.value) {
      formData.append('file', fileControl.value as Blob);
    }

    formData.append('companyName',this.UploadFileForm.value.companyName as string );
    this.companyName = this.UploadFileForm.value.companyName;

    this.showSkeleton = true;  
    this.showSummary = true;
    this.fileuploadService.uploadFiles(formData).subscribe({
      next: (response:any) => {
        this.showSkeleton= false;
        this.analysis = this.convertToHtml(response.msg);

       setTimeout(() => {
        this.startTypingAnimation();
      }, 1000);
      },
      error: (error) => {
        console.error('POST request failed', error);
      }
    });

  }

  private convertToHtml(text: string): string {
    // Convert raw text to HTML
    return text
      .replace(/^\s*---\s*$/gm, '<hr>')
      .replace(/###+\s*(.+)/g, '<h3>$1</h3>') 
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/- (.+)/g, '<li>$1</li>')
      .replace(/\n/g, '<br>'); 
  }

  private startTypingAnimation() {

    const options = {
      strings: [this.analysis], 
      typeSpeed: 0,
      backSpeed: 0,
      loop: false,
      onStringTyped: (arrayPos: number, self: any) => {
        this.typingElement.nativeElement.innerHTML = this.analysis;
      }
    };

    new Typed(this.typingElement.nativeElement, options);
  }


  backToHome() {
    this.showSummary = false;    
    this.UploadFileForm.reset();
  }
}

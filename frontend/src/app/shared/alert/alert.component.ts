import { CommonModule } from '@angular/common';
import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-alert',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alert.component.html',
  styleUrl: './alert.component.scss'
})
export class AlertComponent {

    allErrorTypes = [
      'Error!',
      'Success!',
      "Info!",
      'Warning!'
    ]

    constructor(
      public dialogRef: MatDialogRef<AlertComponent>,
      @Inject(MAT_DIALOG_DATA) public data: { title: string; content: string,type:string,iconType:String,statusCode:any }
    ) {}
  
    onNoClick(): void {
      if(this.data.statusCode == 401) {
        console.log("Will send back to login page");
        // Redirect to login page if 401 error
        window.location.href = 'https://fealtytechnologies.com/';
      }
      this.dialogRef.close();
    }
  }

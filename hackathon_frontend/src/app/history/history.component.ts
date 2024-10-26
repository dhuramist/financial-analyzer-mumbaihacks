import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './history.component.html',
  styleUrl: './history.component.css'
})
export class HistoryComponent {
  files = [
    { name: 'file1.pdf' },
    { name: 'file2.pdf' },
    { name: 'file3.pdf' },
  ];
}

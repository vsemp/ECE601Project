import javax.swing.JFrame;

import java.awt.*;
import javax.swing.*;
import java.awt.event.*;
import java.io.File;

public class UI implements ActionListener{
	
	JFrame frame = new JFrame("EC504");
	JTabbedPane tabPane = new JTabbedPane();
	
	Container con = new Container();
	JLabel label1 = new JLabel("Choose file");
	JTextField text = new JTextField();
	// JTextField text2=new JTextField();
	JButton button = new JButton("...");
	JFileChooser jfc = new JFileChooser();
	
	UI(){
		jfc.setCurrentDirectory(new File("d:\\"));

		frame.setSize(500,250);
		frame.setContentPane(tabPane);
		label1.setBounds(41,29,111,20);
		text.setBounds(164,29,160,20);
		button.setBounds(390,30,50,20);
		button.addActionListener(this);
		con.add(label1);
		con.add(text);
		// con.add(text2);
		con.add(button);
		con.add(jfc);
		tabPane.add("Deduplication",con);
		JButton btnCancel = new JButton("Cancel");//
		btnCancel.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				System.exit(0);//close the window
			}
		});
		btnCancel.setBounds(60, 120, 120, 30);
		con.add(btnCancel);       
		JButton btnOk = new JButton("OK");
		btnOk.addActionListener(new ActionListener() {//
			public void actionPerformed(ActionEvent e) {
				 JOptionPane.showMessageDialog(frame,"go to deduplication,haven't finished yet");// add action to "ok"

			}
		});
		btnOk.setBounds(320, 120, 120, 30);
		con.add(btnOk);
		frame.setVisible(true);
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
	}
	
	public void actionPerformed(ActionEvent e){
		jfc.setFileSelectionMode(0);//locate on files
		int state = jfc.showOpenDialog(null);
		
		if(state == 1){
			return;
		}else{
			File f = jfc.getSelectedFile();
			text.setText(f.getAbsolutePath());
		}
	}

	public static void main(String[] args) {
		new UI();
	}
}
import java.awt.EventQueue;

import javax.swing.JFrame;

import net.proteanit.sql.DbUtils;

import java.sql.*;
import org.jfree.ui.*;
import javax.swing.*;
import java.io.*;
import java.awt.Font;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartUtilities;
import org.jfree.data.*;
import org.jfree.chart.ChartFrame;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.CategoryPlot;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.renderer.category.BarRenderer;
import org.jfree.data.jdbc.JDBCCategoryDataset;


public class sqliteConnection {

    private JFrame frame;
    private JTable table;


    /**
     * Launch the application.
     */

    public static Connection dbConnect(){
        Connection c = null;
        try{
            Class.forName("org.sqlite.JDBC");
            c = DriverManager.getConnection("jdbc:sqlite:D:\\Project\\db.sqlite3");
            System.out.println("Opened database successfully");

        }catch (Exception e){
            System.err.println( e.getClass().getName() + ": " + e.getMessage() );
            System.exit(0);
        }
        return c;
    }
    public static void main(String[] args) {


        EventQueue.invokeLater(new Runnable() {
            public void run() {
                try {
                    sqliteConnection window = new sqliteConnection();
                    window.frame.setVisible(true);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }
    Connection connection = null;
    /**
     * Create the application.
     */
    public sqliteConnection() {
        connection = sqliteConnection.dbConnect();
        initialize();

        }


    /**
     * Initialize the contents of the frame.
     */

    private void initialize() {
        frame = new JFrame();
        frame.setBounds(100, 100, 1260, 698);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.getContentPane().setLayout(null);

        JScrollPane scrollPane = new JScrollPane();
        scrollPane.setBounds(70, 125, 1015, 411);
        frame.getContentPane().add(scrollPane);

        table = new JTable();
        scrollPane.setViewportView(table);

        JButton btnNewButton = new JButton("Load Data");
        btnNewButton.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent arg0) {
                try {
                    String query="select * from mc_measurement";
                    PreparedStatement pst=connection.prepareStatement(query);
                    ResultSet rs=pst.executeQuery();
                    table.setModel(DbUtils.resultSetToTableModel(rs));

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
        btnNewButton.setFont(new Font("Tahoma", Font.BOLD, 18));
        btnNewButton.setBounds(465, 45, 156, 29);
        frame.getContentPane().add(btnNewButton);

        JButton btnNewButton_1 = new JButton("Load Graph");
        btnNewButton_1.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent arg0) {
                try {
                    String query="select id,res from mc_measurement";
                    JDBCCategoryDataset dataset = new JDBCCategoryDataset(sqliteConnection.dbConnect(),query);
                    JFreeChart chart=ChartFactory.createLineChart("Trend Result", "id","res", dataset,PlotOrientation.VERTICAL,false,true,true);
                    BarRenderer renderer = null;
                    CategoryPlot plot = null;
                    renderer = new BarRenderer();
                    ChartFrame frame = new ChartFrame("Trend Result",chart);
                    frame.setVisible(true);
                    frame.setSize(400,650);

                } catch (Exception e) {
                    e.printStackTrace();
                }

            }
        });
        btnNewButton_1.setFont(new Font("Tahoma", Font.BOLD, 18));
        btnNewButton_1.setBounds(825, 46, 150, 29);
        frame.getContentPane().add(btnNewButton_1);
    }
}


